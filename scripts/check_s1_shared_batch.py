"""Replay one physics-produced S1 mixed batch through the v0.3 oracle and C# store."""

import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from google.protobuf import json_format


DOCS = Path(__file__).resolve().parents[1]
PHYSICS = DOCS.parent / "motion-tennis-physics-engine"
GAME = DOCS.parent / "motion-tennis-game-engine"
CASE = DOCS / "fixtures/s1/physics-game-mixed-batch.json"
GAME_TEST = GAME / "tests/MotionTennis.GameState.Tests/MotionTennis.GameState.Tests.csproj"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def output(*args):
    return subprocess.check_output(args, text=True, encoding="utf-8").strip()


def write_json(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode("utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sources(repo, *paths):
    names = output("git", "-C", repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *paths)
    return {f"{repo.name}/{name}": sha256((repo / name).read_bytes().replace(b"\r\n", b"\n"))
            for name in sorted(names.rstrip("\0").split("\0"))}


def game_record(message):
    """Project generated, validated v0.3 fields onto the game's existing typed API."""
    aliases = {"request_seq": "RequestSequence", "velocity_m_s": "VelocityMps"}

    def convert(field, value):
        if field.message_type is not None:
            return game_record(value)
        if field.type == field.TYPE_BYTES:
            return str(uuid.UUID(bytes=value)) if field.name.endswith("session_id") else list(value)
        if field.enum_type is not None and field.enum_type.name == "Team" and value == 0:
            return None
        return value

    record = {}
    for field in message.DESCRIPTOR.fields:
        name = aliases.get(field.name) or "".join(word.capitalize() for word in field.name.split("_"))
        if message.DESCRIPTOR.name == "StateUpdate" and field.name == "match":
            name = "CandidateMatch"
        value = getattr(message, field.name)
        if field.is_repeated:
            record[name] = [convert(field, item) for item in value]
        elif field.message_type is not None and not message.HasField(field.name):
            record[name] = None
        else:
            record[name] = convert(field, value)
    return record


def verify(work):
    schema = DOCS / "spec/motion.proto"
    subprocess.run([sys.executable, "-m", "grpc_tools.protoc", f"-I{schema.parent}",
                    f"--python_out={work}", str(schema)], check=True)
    sys.path[:0] = [str(work), str(DOCS / "tests/match")]
    import motion_pb2 as pb
    from fixtures import build_setup, build_snapshot
    from match_contract import OfflineMatchStore, encoded, transaction_key

    setup = build_setup(pb)
    build = work / "physics-build"
    subprocess.run(["cmake", "-S", PHYSICS, "-B", build, "-DCMAKE_BUILD_TYPE=Release",
                    "-DMOTION_TENNIS_BUILD_TESTS=ON"], check=True)
    subprocess.run(["cmake", "--build", build, "--config", "Release", "--target", "s1_game_fixture"], check=True)
    filename = "s1_game_fixture.exe" if os.name == "nt" else "s1_game_fixture"
    binary = build / "Release" / filename
    if not binary.is_file():
        binary = build / filename
    actual = json.loads(output(binary, setup.configuration_sha256.hex()))
    write_json(work / "physics-output.json", actual)
    expected = json.loads(CASE.read_text(encoding="utf-8"))

    def checked_message(name, message_type):
        emitted = json_format.ParseDict(actual[name], message_type())
        reference = json_format.ParseDict(expected[name], message_type())
        check(emitted == reference, f"Physics {name} differs from the shared fixture")
        return emitted

    config = checked_message("configuration", pb.MatchConfiguration)
    snapshot = checked_message("snapshot", pb.Snapshot)
    query = checked_message("query", pb.BallStateRequest)
    update = checked_message("update", pb.StateUpdate)
    check(config == setup.configuration, "Physics roster or rules differ from the canonical configuration")
    check(snapshot == build_snapshot(pb, setup), "Physics initial snapshot differs from the canonical version-one state")
    check(actual["rejected"] == expected["rejected"] and len(actual["rejected"]) == 1,
          "Expected the pinned rejection observation")
    rejection = actual["rejected"][0]
    rejected_tx = json_format.ParseDict(rejection["transaction"], pb.Transaction())
    check(len(query.queries) == 3 and query.queries[1].transaction == rejected_tx and
          query.queries[1].query_id == rejection["query_id"] and rejection["outcome"] == pb.STALE_INPUT,
          "The rejection must name the middle query and its stale input")
    check([d.transaction for d in update.decisions] == [query.queries[0].transaction, query.queries[2].transaction]
          and [d.outcome for d in update.decisions] == [pb.HIT, pb.MISS], "Unexpected surviving decisions")
    oracle = OfflineMatchStore(setup, snapshot)
    check(oracle.query(query).snapshot == snapshot, "Oracle query returned a different snapshot")
    accepted = oracle.commit(update, [transaction_key(rejected_tx)])
    check(accepted.status == pb.ACCEPTED and oracle.snapshot.match == update.match,
          f"Shared oracle did not commit the physics candidate: {accepted.reason}")

    game_setup = game_record(setup)
    game_setup["CanonicalConfigurationBytes"] = list(encoded(config))
    writer = {"GameSessionId": game_setup["GameSessionId"], "WriterEpoch": setup.writer_epoch,
              "PhysicsControlSessionId": "10000000-0000-4000-8000-000000000001"}
    game_input = work / "game-input.json"
    write_json(game_input, {"writer": writer, "setup": game_setup, "snapshot": game_record(snapshot),
                            "query": game_record(query), "update": game_record(update),
                            "rejected": [{"QueryId": rejection["query_id"], "Transaction": game_record(rejected_tx),
                                          "Outcome": rejection["outcome"], "ObservedPiUs": rejection["observed_pi_us"]}]})
    game_bin = work / "game-bin"
    subprocess.run(["dotnet", "build", GAME_TEST, "-c", "Release", "-o", game_bin], check=True)
    receipt = json.loads(output("dotnet", game_bin / "MotionTennis.GameState.Tests.dll", "--shared-batch", game_input))
    check(receipt["status"] == "passed" and receipt["state_version"] == accepted.state_version
          and receipt["simulation_tick"] == accepted.simulation_tick and receipt["rejected_count"] == 1
          and receipt["decision_count"] == 2, "Game result disagrees with the shared oracle")
    check((uuid.UUID(receipt["game_session_id"]).bytes, receipt["writer_epoch"], receipt["batch_id"]) ==
          (query.game_session_id, query.writer_epoch, query.batch_id), "Game received a different batch identity")

    def receipt_key(row):
        tx = row["Transaction"]
        return tx["ControllerId"], uuid.UUID(tx["SessionId"]).bytes, tx["RequestSequence"]

    check([(r["EventIndex"], receipt_key(r), r["Outcome"]) for r in receipt["accepted_decisions"]] ==
          [(d.event_index, transaction_key(d.transaction), d.outcome) for d in update.decisions],
          "Game accepted different survivor identities, order or outcomes")
    check([(r["QueryId"], receipt_key(r), r["Outcome"], r["ObservedPiUs"]) for r in receipt["rejected"]] ==
          [(rejection["query_id"], transaction_key(rejected_tx), rejection["outcome"], rejection["observed_pi_us"])],
          "Game received different rejected-input evidence")
    controls = {"missing_rejection", "wrong_rejection", "duplicate_rejection", "missing_survivor",
                "reordered_survivors", "changed_retry_accounting"}
    check(controls <= set(receipt["negative_cases"]), "Game did not exercise all accounting controls")
    return {
        "case": CASE.name, "physics_base": output("git", "-C", PHYSICS, "rev-parse", "HEAD"),
        "game_base": output("git", "-C", GAME, "rev-parse", "HEAD"),
        "documentation_base": output("git", "-C", DOCS, "rev-parse", "HEAD"),
        "tools": {"python": sys.version.split()[0], "protobuf": version("protobuf"),
                  "grpcio-tools": version("grpcio-tools"), "cmake": output("cmake", "--version").splitlines()[0],
                  "dotnet_sdk": output("dotnet", "--version")},
        "source_sha256_lf": {
            **sources(PHYSICS, "CMakeLists.txt", "include", "src", "tests/fixtures.hpp",
                      "tests/s1_game_fixture.cpp", "tests/fixture_proto_json.hpp"),
            **sources(GAME, "src", "tests"),
            **sources(DOCS, "spec/motion.proto", "spec/reference-profile.json", "scripts/check_s1_shared_batch.py",
                      "scripts/match_contract.py", "tests/match/fixtures.py")},
        "canonical_protobuf_sha256": {msg.DESCRIPTOR.name: sha256(encoded(msg)) for msg in
                                      (config, snapshot, query, update)},
        "fixture_sha256_lf": sha256(CASE.read_bytes().replace(b"\r\n", b"\n")),
        "oracle": {"state_version": accepted.state_version, "simulation_tick": accepted.simulation_tick},
        "game": receipt,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True, help="Build directory for scratch files and replay inputs")
    parser.add_argument("--report", type=Path, help="Also save the verified result as JSON")
    args = parser.parse_args()
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    report = verify(work)
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
