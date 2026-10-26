#!/usr/bin/env python3
"""Generate and test bounded Python/C codecs for the S0 contract, offline."""

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, *, env=None):
    result = subprocess.run(command, text=True, capture_output=True, env=env, cwd=ROOT)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str, command))}\n{result.stdout}{result.stderr}")
    return result.stdout


def verify_dependencies(nanopb_root):
    versions = {}
    for line in (HERE / "requirements.txt").read_text().splitlines():
        name, expected = line.split("==")
        actual = importlib.metadata.version(name)
        if actual != expected:
            raise ValueError(f"{name}: expected {expected}, found {actual}")
        versions[name] = actual
    lock = json.loads((HERE / "nanopb-source.lock.json").read_text())
    for name, expected in lock["files"].items():
        if digest(nanopb_root / name) != expected:
            raise ValueError(f"Unpinned nanopb source file: {name}")
    versions["nanopb_c_archive_sha256"] = lock["archive_sha256"]
    return versions


def generate_python(schema, output):
    run([sys.executable, "-m", "grpc_tools.protoc", f"-I{schema.parent}",
         f"--python_out={output}", str(schema)])
    sys.path.insert(0, str(output))
    return importlib.import_module(schema.stem + "_pb2")


def compile_c(module, profile, generated, nanopb_root, cc, update_options):
    from wire_bounds import nanopb_options
    options = nanopb_options(module, profile)
    options_path = HERE / "motion.options"
    if update_options:
        options_path.write_text(options)
    if not options_path.exists() or options_path.read_text() != options:
        raise ValueError("motion.options is stale; review the profile and run --update-options")
    (generated / "motion.options").write_text(options)
    plugin = Path(sys.executable).parent / "protoc-gen-nanopb"
    if not plugin.exists():
        raise ValueError("Missing protoc-gen-nanopb in the current Python environment")
    run([sys.executable, "-m", "grpc_tools.protoc", f"-I{ROOT / 'spec'}",
         f"--plugin=protoc-gen-nanopb={plugin}",
         f"--nanopb_out=-I{generated}:{generated}", str(ROOT / "spec/motion.proto")])
    if "pb_callback_t" in (generated / "motion.pb.h").read_text():
        raise ValueError("Unbounded callback field in generated contract codec")
    lines = [f"#define CONTRACT_FRAME_LIMIT {profile['limits']['maximum_stream_frame_bytes']}",
             "static void print_contract_resources(void) {", '    printf("{");']
    for index, descriptor in enumerate(module.DESCRIPTOR.message_types_by_name.values()):
        prefix = "," if index else ""
        name = descriptor.full_name.replace(".", "_")
        lines.append(f'    printf("{prefix}\\\"{descriptor.name}\\\":%zu", sizeof({name}));')
    lines.extend(['    printf("}\\n");', "}"])
    (generated / "contract_resources.h").write_text("\n".join(lines) + "\n")
    executable = generated / "codec_harness"
    environment = dict(os.environ, CCACHE_DISABLE="1")
    command = [cc, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-DPB_FIELD_32BIT", "-DPB_VALIDATE_UTF8",
               f"-I{nanopb_root}", f"-I{generated}", str(HERE / "codec_harness.c"),
               str(generated / "motion.pb.c"), str(nanopb_root / "pb_common.c"),
               str(nanopb_root / "pb_encode.c"), str(nanopb_root / "pb_decode.c"),
               "-o", str(executable)]
    run(command, env=environment)
    resources = json.loads(run([str(executable), "--resources"]))
    return executable, resources


class CodecChecks:
    def __init__(self, module, executable, temporary):
        self.module = module
        self.executable = executable
        self.temporary = temporary
        self.results = []

    def roundtrip(self, name, envelope):
        original = envelope.SerializeToString(deterministic=True)
        decoded = self.module.Envelope.FromString(original)
        if decoded != envelope:
            raise AssertionError(f"Python roundtrip changed {name}")
        source = self.temporary / "input.bin"
        destination = self.temporary / "output.bin"
        source.write_bytes(original)
        run([str(self.executable), str(source), str(destination)])
        c_bytes = destination.read_bytes()
        c_decoded = self.module.Envelope.FromString(c_bytes)
        if c_decoded != envelope:
            raise AssertionError(f"C roundtrip changed {name}")
        if c_bytes != original:
            raise AssertionError(f"C and Python canonical encodings differ for {name}")
        result = {"name": name, "bytes": len(original),
                  "sha256": hashlib.sha256(original).hexdigest(), "python_c_equal": True}
        self.results.append(result)
        return result

    def reject_c(self, name, data):
        source = self.temporary / "rejected.bin"
        destination = self.temporary / "should-not-exist.bin"
        source.write_bytes(data)
        result = subprocess.run([str(self.executable), str(source), str(destination)],
                                capture_output=True, text=True)
        if result.returncode != 1:
            raise AssertionError(f"Expected bounded C decoder rejection for {name}: {result.stderr}")
        return {"name": name, "rejected_by": "bounded_nanopb_harness"}


def allocation_model(sizes, maximums, profile):
    """Conservative contract payload storage, not complete runtime/device RAM."""
    limits = profile["limits"]
    players = profile["players"]
    largest_encoded = max(value["encoded_bytes"] for value in maximums.values())
    common = {
        "decoded_envelopes": 2 * sizes["Envelope"],
        "bounded_raw_envelopes": 2 * largest_encoded,
    }
    pending = limits["controller_pending_transactions"]
    controller = dict(common,
                      pending_input_and_result_payloads=pending * (sizes["ControllerInput"] + sizes["FeedbackResult"]),
                      pending_bookkeeping=pending * 64)
    state_io = (limits["state_stream_outbound_frames"] + limits["state_stream_inbound_frames"]) * (limits["state_stream_frame_bytes"] + 4)
    dedup_record = sum(sizes[name] for name in ("BallStateRequest", "BallStateResponse", "StateUpdate", "StateCommitResult")) + 64
    physics = dict(common,
                   state_framing=state_io,
                   input_queue=players * limits["physics_queue_per_controller"] * sizes["ControllerInput"],
                   imu_history=players * limits["imu_history_samples_per_controller"] * sizes["ControllerInput"],
                   pose_history=players * limits["pose_history_frames_per_person"] * sizes["SkeletonFrame"],
                   batch_scratch=2 * sizes["StateUpdate"] + sizes["BallStateResponse"],
                   dedup_payloads=limits["dedup_batches"] * dedup_record)
    game = dict(common,
                state_framing=state_io,
                committed_and_candidate_snapshots=2 * sizes["Snapshot"],
                setup=sizes["MatchSetup"],
                dedup_payloads=limits["dedup_batches"] * dedup_record)
    models = {"controller_contract_storage": controller,
              "physics_contract_storage": physics, "game_contract_storage": game}
    budgets = profile["contract_memory_budgets_bytes"]
    if sizes["Envelope"] > budgets["generated_envelope"]:
        raise AssertionError("Generated Envelope exceeds its storage budget")
    results = {}
    for name, components in models.items():
        total = sum(components.values())
        if total > budgets[name]:
            raise AssertionError(f"{name}: {total} exceeds {budgets[name]}")
        results[name] = {"components_bytes": components, "total_bytes": total,
                         "budget_bytes": budgets[name], "within_budget": True}
    return {
        "models": results,
        "largest_encoded_envelope_bytes": largest_encoded,
        "dedup_record_bytes": dedup_record,
        "dedup_record_formula": "sizeof(BallStateRequest)+sizeof(BallStateResponse)+sizeof(StateUpdate)+sizeof(StateCommitResult)+64",
        "pending_bookkeeping_allowance_bytes_per_entry": 64,
        "limitations": [
            "Host ABI sizeof evidence; ESP32, Pi and Windows ABIs are not measured.",
            "Payload, bounded framing and declared bookkeeping only; no firmware, OS, network-stack, heap, code or call-stack sizing.",
            "Allocation of a control frame is capped by the maximum known bounded Envelope; the outer 65536-byte transport ceiling is not an allocation instruction.",
            "Capture image/inference buffers and runtime logging are outside this contract-storage model.",
        ],
    }


def source_hashes():
    paths = [ROOT / "spec/motion.proto", ROOT / "spec/reference-profile.json"]
    for directory in (HERE, ROOT / "tests/contract", ROOT / "tests/match"):
        paths.extend(path for path in directory.rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    paths.append(ROOT / "scripts/match_contract.py")
    return {str(path.relative_to(ROOT)): digest(path) for path in sorted(set(paths)) if path.exists()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nanopb-root", type=Path, required=True)
    parser.add_argument("--cc", default="gcc")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--update-options", action="store_true", help="Regenerate reviewed static field bounds")
    parser.add_argument("--codec-only", action="store_true", help="Development-only; omit semantic checks and mark report incomplete")
    args = parser.parse_args()
    nanopb_root = args.nanopb_root.resolve()
    dependencies = verify_dependencies(nanopb_root)
    profile = json.loads((ROOT / "spec/reference-profile.json").read_text())
    from wire_bounds import body_transport, fill_maximum, validate_fields
    with tempfile.TemporaryDirectory(prefix="motion-tennis-s0-") as temporary_name:
        temporary = Path(temporary_name)
        module = generate_python(ROOT / "spec/motion.proto", temporary)
        executable, sizes = compile_c(module, profile, temporary, nanopb_root, args.cc, args.update_options)
        codec = CodecChecks(module, executable, temporary)
        maximums = {}
        for field in module.Envelope.DESCRIPTOR.oneofs_by_name["body"].fields:
            envelope = fill_maximum(module.Envelope(), profile)
            fill_maximum(getattr(envelope, field.name), profile)
            validate_fields(envelope, profile)
            result = codec.roundtrip("structural_maximum_" + field.name, envelope)
            transport, cap = body_transport(field.name, profile)
            if result["bytes"] > cap:
                raise AssertionError(f"{field.name}: {result['bytes']} exceeds {cap}")
            maximums[field.name] = {"encoded_bytes": result["bytes"], "transport": transport,
                                    "transport_limit_bytes": cap, "margin_bytes": cap - result["bytes"]}
        sys.path.insert(0, str(ROOT / "tests/contract"))
        from test_generated import high_width_fixture, run_generated_checks
        generated_results = run_generated_checks(module, profile, codec)
        legacy = generate_python(ROOT / "tests/contract/fixtures/legacy_motion_v02.proto", temporary)
        legacy_results = {}
        for name in ("state_update", "state_publication"):
            envelope = fill_maximum(legacy.Envelope(), profile)
            fill_maximum(getattr(envelope, name), profile)
            raw = envelope.SerializeToString(deterministic=True)
            legacy_results[name] = {"structural_bound_bytes": len(raw),
                                    "exceeds_legacy_udp_cap": len(raw) > 1200}
        semantic_result = {"status": "not_run", "tests": 0}
        if not args.codec_only:
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPATH"] = os.pathsep.join([str(temporary), str(ROOT / "scripts"), str(HERE)])
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests/match", "-v"],
                                    cwd=ROOT, env=environment, text=True, capture_output=True)
            output = result.stdout + result.stderr
            print(output, file=sys.stderr, end="")
            if result.returncode:
                raise AssertionError("Full-match semantic checks failed")
            count_match = re.search(r"Ran (\d+) tests?", output)
            if not count_match or int(count_match.group(1)) == 0:
                raise AssertionError("No full-match semantic tests ran")
            semantic_result = {"status": "passed", "tests": int(count_match.group(1))}
            sys.path.insert(0, str(ROOT / "tests/match"))
            sys.path.insert(0, str(ROOT / "scripts"))
            from fixtures import build_setup, build_snapshot, build_update, build_query
            from match_contract import validate_query, validate_response, validate_setup, validate_update
            setup = build_setup(module)
            validate_setup(setup)
            regular_query = build_query(module, setup)
            periodic_query = build_query(module, setup, periodic=True)
            regular_update = build_update(module, setup)
            periodic_update = build_update(module, setup, periodic=True)
            validate_query(regular_query, setup)
            validate_query(periodic_query, setup)
            validate_update(regular_update, setup, regular_query)
            validate_update(periodic_update, setup, periodic_query)
            semantic_fixtures = [
                ("full_match_setup", "match_setup", setup),
                ("eight_query_request", "ball_state_request", regular_query),
                ("eight_decision_update", "state_update", regular_update),
                ("periodic_only_query", "ball_state_request", periodic_query),
                ("periodic_only_update", "state_update", periodic_update),
            ]
            response = module.BallStateResponse(game_session_id=setup.game_session_id,
                                                batch_id=regular_query.batch_id,
                                                status=module.QUERY_OK, writer_epoch=regular_query.writer_epoch)
            response.snapshot.CopyFrom(build_snapshot(module, setup))
            response.queries.extend(regular_query.queries)
            validate_response(response, setup, regular_query)
            semantic_fixtures.append(("full_snapshot_response", "ball_state_response", response))
            large_setup, large_query, large_update = high_width_fixture(module, build_setup, build_query, build_update)
            validate_setup(large_setup)
            validate_query(large_query, large_setup)
            validate_update(large_update, large_setup, large_query)
            semantic_fixtures.extend([
                ("high_width_valid_setup", "match_setup", large_setup),
                ("high_width_valid_eight_query_request", "ball_state_request", large_query),
                ("high_width_valid_eight_decision_update", "state_update", large_update),
            ])
            for name, body, value in semantic_fixtures:
                envelope = module.Envelope(major=0, minor=3, sender_id=1,
                                           sender_session_id=b"s" * 16, message_seq=1,
                                           sent_time_us=1000000, clock_id=1, run_id=b"r" * 16)
                getattr(envelope, body).CopyFrom(value)
                from wire_bounds import validate_envelope
                validate_envelope(envelope, profile)
                codec.roundtrip(name, envelope)
        report = {
            "status": "codec_only_incomplete" if args.codec_only else "passed_offline_contract_checks",
            "scope": "Generated-codec and contract-fixture proof; no runtime or hardware implementation",
            "schema_sha256": digest(ROOT / "spec/motion.proto"),
            "profile_sha256": digest(ROOT / "spec/reference-profile.json"),
            "environment": {"python": platform.python_version(), "system": platform.system(),
                            "machine": platform.machine(), "compiler": run([args.cc, "--version"]).splitlines()[0],
                            "protoc": run([sys.executable, "-m", "grpc_tools.protoc", "--version"]).strip(),
                            "dependencies": dependencies},
            "maximum_encoded_messages": maximums,
            "maximum_method": "Conservative structural upper bounds: all optional fields present, each repeated/byte/string field at its bound, uint64 at 2^56-1, uint32 at 2^32-1, largest declared enum. These witnesses are not valid gameplay states; every admitted state is no larger.",
            "roundtrips": codec.results,
            "negative_and_envelope_checks": generated_results,
            "semantic_checks": semantic_result,
            "generated_c_struct_bytes": sizes,
            "generated_c_compile_flags": ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-DPB_FIELD_32BIT", "-DPB_VALIDATE_UTF8"],
            "harness_only_static_raw_buffers_bytes": 2 * profile["limits"]["maximum_stream_frame_bytes"],
            "allocation_model": allocation_model(sizes, maximums, profile),
            "legacy_v02": {"baseline_revision": "95c2592", "measurements": legacy_results,
                           "qualification": "Conservative structural bounds only. These do not prove a semantically admitted legacy message exceeded the UDP cap."},
            "source_sha256": source_hashes(),
            "limitations": ["Host Linux Python/C interoperability only; ESP32/Pi/Windows runtime and compiler checks remain later stages.",
                            "No timing, WLAN, hardware, tracking accuracy or complete tennis-rule proof.",
                            "S0 acceptance remains a separate recorded human decision."],
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"Contract checks: {report['status']}; {len(codec.results)} Python/C roundtrips, "
              f"{len(generated_results)} rejection/envelope cases, {semantic_result['tests']} semantic tests")
        print(f"Generated Envelope: {sizes['Envelope']} bytes; largest encoded envelope: "
              f"{max(value['encoded_bytes'] for value in maximums.values())} bytes")
        if args.report:
            print(f"Evidence: {args.report}")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, RuntimeError, OSError, importlib.metadata.PackageNotFoundError) as error:
        raise SystemExit(str(error)) from error
