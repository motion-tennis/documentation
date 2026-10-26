"""Offline v0.3 contract oracle; no transport, simulation or tennis-rule engine.

Generated ``motion_pb2`` is supplied by the contract checker. The oracle accepts
complete externally prepared candidates. It never calculates hits, scores,
movement, clock mappings or hardware outcomes.
"""

from collections import Counter
from dataclasses import dataclass
import hashlib
import math

import motion_pb2 as pb


MAX_UINT64 = (1 << 56) - 1
SLOTS = {1, 2, 3, 4}
AWARD_EVENTS = {pb.POINT_AWARDED, pb.GAME_AWARDED, pb.SET_AWARDED, pb.MATCH_AWARDED}


class ContractError(ValueError):
    """An offline fixture violates the shared semantic contract."""


def require(condition, reason):
    if not condition:
        raise ContractError(reason)


def encoded(message):
    return message.SerializeToString(deterministic=True)


def clone(message):
    result = type(message)()
    result.CopyFrom(message)
    return result


def validate_scalars(message):
    """Reject unknown fields/enums, nonfinite numbers and oversized uint64s."""
    clean = clone(message)
    clean.DiscardUnknownFields()
    require(encoded(clean) == encoded(message), "unknown fields are not canonical")
    for field, value in message.ListFields():
        values = value if field.is_repeated else [value]
        for item in values:
            if field.type == field.TYPE_MESSAGE:
                validate_scalars(item)
            elif field.type == field.TYPE_UINT64:
                require(item <= MAX_UINT64, f"{field.full_name}: uint64 bound")
            elif field.type in (field.TYPE_FLOAT, field.TYPE_DOUBLE):
                require(math.isfinite(item), f"{field.full_name}: nonfinite value")
            elif field.type == field.TYPE_ENUM:
                require(item in field.enum_type.values_by_number, f"{field.full_name}: unknown enum")
            elif field.type == field.TYPE_STRING:
                require("\x00" not in item, f"{field.full_name}: embedded NUL is not a static C string")


def present(message, *names):
    for name in names:
        require(message.HasField(name), f"missing {message.DESCRIPTOR.name}.{name}")


def uuid(value, name):
    require(len(value) == 16, f"{name}: UUID must have 16 bytes")


def positive(value, name):
    require(value > 0, f"{name}: nonzero identity required")


def team(slot):
    require(slot in SLOTS, "unknown player slot")
    return pb.TEAM_A if slot <= 2 else pb.TEAM_B


def configuration_hash(configuration):
    validate_scalars(configuration)
    return hashlib.sha256(encoded(configuration)).digest()


def validate_setup(setup):
    validate_scalars(setup)
    positive(setup.command_id, "command_id")
    positive(setup.writer_epoch, "setup writer epoch")
    uuid(setup.game_session_id, "game_session_id")
    present(setup, "configuration")
    config = setup.configuration
    present(config, "rules")
    positive(config.roster_revision, "roster_revision")
    positive(config.rules_revision, "rules_revision")
    require([p.player_slot for p in config.players] == [1, 2, 3, 4],
            "configuration needs canonical ordered slots 1..4")
    require(len({p.controller_id for p in config.players}) == 4,
            "controller occupies multiple slots")
    require(len({(p.tracking_session_id, p.person_id) for p in config.players}) == 4,
            "tracked person occupies multiple slots")
    require(len({p.tracking_session_id for p in config.players}) == 1,
            "one tracker session is required by the shared batch field")
    require(len({p.physical_station_id for p in config.players}) == 4,
            "physical stations must be distinct")
    require(len({p.avatar_id for p in config.players}) == 4, "avatar occupies multiple slots")
    for player in config.players:
        uuid(player.controller_session_id, "controller_session_id")
        uuid(player.tracking_session_id, "tracking_session_id")
        for name in ("controller_id", "person_id", "association_version",
                     "calibration_id", "physical_station_id", "avatar_id"):
            positive(getattr(player, name), name)
    rules = config.rules
    require(rules.sets_to_win in (1, 2, 3), "sets_to_win must be 1, 2 or 3")
    require((rules.games_to_win_set, rules.minimum_game_lead, rules.tiebreak_at_games,
             rules.tiebreak_points_to_win, rules.tiebreak_minimum_lead) == (6, 2, 6, 7, 2),
            "unsupported scoring profile")
    require(rules.final_set_tiebreak, "baseline requires final-set tiebreak")
    require(len(rules.tuning_sha256) == 32, "tuning hash must have 32 bytes")
    require(setup.configuration_sha256 == configuration_hash(config), "configuration hash mismatch")
    require(len(setup.reason.encode("utf-8")) <= 128, "setup reason too long")
    require(setup.response or not setup.accepted, "setup request cannot claim acceptance")


def validate_score(score, rules):
    require(not (score.points_a == pb.ADVANTAGE and score.points_b != pb.FORTY),
            "advantage A requires forty B")
    require(not (score.points_b == pb.ADVANTAGE and score.points_a != pb.FORTY),
            "advantage B requires forty A")
    require(len(score.completed_sets) <= 2 * rules.sets_to_win - 1,
            "too many completed sets")
    wins = Counter()
    for completed in score.completed_sets:
        require(wins[pb.TEAM_A] < rules.sets_to_win and wins[pb.TEAM_B] < rules.sets_to_win,
                "set recorded after match completion")
        high, low = sorted((completed.games_a, completed.games_b), reverse=True)
        require((high == 6 and low <= 4) or (high == 7 and low in (5, 6)),
                "invalid completed set score")
        require(completed.had_tiebreak == (low == 6), "set tiebreak flag disagrees with games")
        if completed.had_tiebreak:
            high_points, low_points = sorted(
                (completed.tiebreak_points_a, completed.tiebreak_points_b), reverse=True)
            require(high_points == max(7, low_points + 2), "invalid completed tiebreak score")
            require((completed.games_a > completed.games_b) ==
                    (completed.tiebreak_points_a > completed.tiebreak_points_b),
                    "tiebreak winner disagrees with set winner")
        else:
            require(not completed.tiebreak_points_a and not completed.tiebreak_points_b,
                    "non-tiebreak set has tiebreak points")
        wins[pb.TEAM_A if completed.games_a > completed.games_b else pb.TEAM_B] += 1
    require((score.sets_a, score.sets_b) == (wins[pb.TEAM_A], wins[pb.TEAM_B]),
            "set totals disagree with completed sets")
    require(score.games_a <= 7 and score.games_b <= 7, "current game count exceeds baseline")
    if score.tiebreak:
        require(score.games_a == score.games_b == 6, "tiebreak requires six games each")
        require(score.points_a == score.points_b == pb.LOVE, "tiebreak has standard-game points")
    else:
        require(not score.tiebreak_points_a and not score.tiebreak_points_b,
                "standard game has tiebreak points")


def validate_match_state(state, setup):
    validate_scalars(state)
    present(state, "ball", "serve", "rally", "score")
    present(state.ball, "position_m", "velocity_m_s")
    require(state.ball.radius_m > 0, "ball radius must be positive")
    positive(state.ball.calibration_id, "ball calibration")
    config = setup.configuration
    require((state.roster_revision, state.rules_revision, state.configuration_sha256) ==
            (config.roster_revision, config.rules_revision, setup.configuration_sha256),
            "state configuration/revision mismatch")
    require([a.player_slot for a in state.avatars] == [1, 2, 3, 4],
            "state needs canonical ordered avatars 1..4")
    for avatar in state.avatars:
        present(avatar, "position_m", "velocity_m_s", "target_m")
        require(avatar.movement != pb.MOVEMENT_UNSPECIFIED, "movement is unspecified")
        require(avatar.coverage_owner_slot == 0 or
                team(avatar.coverage_owner_slot) == team(avatar.player_slot),
                "coverage owner belongs to wrong team")
    serve = state.serve
    require(serve.phase != pb.SERVE_UNSPECIFIED, "serve phase is unspecified")
    require(team(serve.server_slot) != team(serve.receiver_slot), "server and receiver share a team")
    require(serve.side in (pb.DEUCE_SIDE, pb.AD_SIDE), "service side is unspecified")
    require(serve.attempt in (1, 2), "serve attempt must be first or second")
    require(len(serve.service_order) == 4 and set(serve.service_order) == SLOTS,
            "service order must contain every slot once")
    require(all(team(serve.service_order[i]) != team(serve.service_order[(i + 1) % 4])
                for i in range(4)), "service order must alternate teams")
    require(len(serve.receiving_order) == 4 and set(serve.receiving_order[:2]) == {1, 2}
            and set(serve.receiving_order[2:]) == {3, 4}, "invalid receiving order")
    require(serve.service_turn_index < 4, "invalid service turn index")
    require(serve.server_slot == serve.service_order[serve.service_turn_index],
            "server disagrees with service turn")
    require(serve.tiebreak_first_server_slot in (SLOTS if state.score.tiebreak else SLOTS | {0}),
            "missing or invalid tiebreak rotation anchor")
    receiving_index = (2 if team(serve.server_slot) == pb.TEAM_A else 0)
    receiving_index += int(serve.side == pb.AD_SIDE)
    require(serve.receiver_slot == serve.receiving_order[receiving_index],
            "receiver disagrees with service side/order")
    if serve.phase in (pb.SERVE_TOSS, pb.SERVE_CONTACT, pb.SERVE_IN_FLIGHT):
        positive(serve.toss_id, "toss_id")
    require(state.rally.last_hitter_slot in SLOTS | {0}, "invalid last hitter")
    require(state.rally.bounce_count <= 2, "bounce count exceeds terminal second bounce")
    require(state.rally.contact_slot_mask <= 15, "contact mask exceeds four slots")
    positive(state.point_id, "point_id")
    uuid(state.pi_reference_session_id, "Pi reference session")
    positive(state.pi_reference_clock_id, "Pi reference clock")
    require(state.phase != pb.MATCH_UNSPECIFIED, "match phase is unspecified")
    validate_score(state.score, config.rules)
    completed_winner = (pb.TEAM_A if state.score.sets_a == config.rules.sets_to_win else
                        pb.TEAM_B if state.score.sets_b == config.rules.sets_to_win else pb.TEAM_NONE)
    require((state.phase == pb.MATCH_FINISHED) == (completed_winner != pb.TEAM_NONE),
            "match completion disagrees with set totals")
    require(state.winner == completed_winner, "match winner disagrees with set totals")


def transaction_key(transaction):
    positive(transaction.controller_id, "controller_id")
    uuid(transaction.session_id, "controller session")
    positive(transaction.request_seq, "request_seq")
    return transaction.controller_id, transaction.session_id, transaction.request_seq


def validate_query(query, setup):
    validate_scalars(query)
    require(query.game_session_id == setup.game_session_id, "query game session mismatch")
    positive(query.writer_epoch, "writer epoch")
    positive(query.batch_id, "batch_id")
    require(len(query.queries) <= 8, "more than eight queries")
    roster = {(p.controller_id, p.controller_session_id) for p in setup.configuration.players}
    keys, query_ids, counts = set(), set(), Counter()
    for entry in query.queries:
        present(entry, "transaction")
        key = transaction_key(entry.transaction)
        require(key[:2] in roster, "query controller/session absent from roster")
        positive(entry.query_id, "query_id")
        require(key not in keys and entry.query_id not in query_ids, "duplicate query identity")
        keys.add(key)
        query_ids.add(entry.query_id)
        counts[key[0]] += 1
    require(all(count <= 2 for count in counts.values()), "more than two queries per controller")


def validate_response(response, setup, query):
    validate_scalars(response)
    require((response.game_session_id, response.writer_epoch, response.batch_id) ==
            (query.game_session_id, query.writer_epoch, query.batch_id), "response/query identity mismatch")
    require([encoded(entry) for entry in response.queries] ==
            [encoded(entry) for entry in query.queries], "response does not echo exact queries")
    require(len(response.reason.encode("utf-8")) <= 128, "query rejection reason too long")
    if response.status == pb.QUERY_OK:
        present(response, "snapshot")
        require(response.snapshot.game_session_id == response.game_session_id,
                "response snapshot game session mismatch")
        require(response.snapshot.tick_duration_us == 5000, "snapshot tick duration mismatch")
        present(response.snapshot, "match")
        validate_match_state(response.snapshot.match, setup)
    else:
        require(response.status == pb.QUERY_REJECTED, "query status is unspecified")
        require(bool(response.reason), "query rejection needs a reason")
        require(not response.HasField("snapshot"), "rejected query cannot supply a usable snapshot")


def validate_update(update, setup, query, rejected_keys=()):
    """Validate correlation; rejected inputs are an explicit test-oracle handoff."""
    validate_scalars(update)
    validate_query(query, setup)
    require((update.game_session_id, update.writer_epoch, update.batch_id) ==
            (query.game_session_id, query.writer_epoch, query.batch_id), "update/query identity mismatch")
    present(update, "match")
    validate_match_state(update.match, setup)
    require(len(update.decisions) <= 8 and len(update.rule_events) <= 16, "batch collection bound")
    source_keys = [transaction_key(entry.transaction) for entry in query.queries]
    rejected = set(rejected_keys)
    require(rejected <= set(source_keys), "rejection does not name a source query")
    actual_keys = [transaction_key(decision.transaction) for decision in update.decisions]
    require(actual_keys == [key for key in source_keys if key not in rejected],
            "decisions must exactly preserve surviving source query order")
    roster = {(p.controller_id, p.controller_session_id): p for p in setup.configuration.players}
    for index, decision in enumerate(update.decisions):
        require(decision.event_index == index, "decision indices must be contiguous from zero")
        require(decision.outcome in (pb.HIT, pb.MISS), "only hit/miss may commit")
        for name in ("current_sample_id", "pose_frame_id", "person_id", "association_version"):
            positive(getattr(decision, name), name)
        binding = roster[transaction_key(decision.transaction)[:2]]
        require((decision.person_id, decision.association_version, update.tracking_session_id) ==
                (binding.person_id, binding.association_version, binding.tracking_session_id),
                "decision tracking/association provenance mismatch")
        present(decision, "cue")
        cue = decision.cue
        require(0 <= cue.intensity <= 1, "cue intensity out of range")
        if cue.electrical_eligible:
            positive(cue.cue_id, "cue_id")
            positive(cue.duration_ms, "cue duration")
            require(cue.kind == (pb.CUE_HIT if decision.outcome == pb.HIT else pb.CUE_MISS),
                    "cue kind disagrees with outcome")
        else:
            require(cue.kind == pb.CUE_NONE, "ineligible cue must be none")
    previous_event_tick = 0
    for index, event in enumerate(update.rule_events, start=8):
        require(event.event_index == index, "rule event indices must be contiguous from eight")
        require(event.kind != pb.RULE_UNSPECIFIED, "rule event kind is unspecified")
        positive(event.point_id, "event point_id")
        require(event.player_slot in SLOTS | {0}, "invalid event slot")
        require(previous_event_tick <= event.simulation_tick <= update.target_simulation_tick,
                "event ticks must be ordered and no later than the target tick")
        previous_event_tick = event.simulation_tick
        require(event.serve_attempt in (0, 1, 2), "invalid event serve attempt")
        if event.has_cause:
            require(event.cause_decision_index < len(update.decisions), "missing event cause decision")
        else:
            require(event.cause_decision_index == 0, "periodic event has a fabricated cause")
        if event.kind in AWARD_EVENTS:
            require(event.team in (pb.TEAM_A, pb.TEAM_B), "award requires winning team")
        if event.kind == pb.TECHNICAL_PAUSE:
            require(event.team == pb.TEAM_NONE, "technical pause cannot award a team")


@dataclass(frozen=True)
class CommitResult:
    status: int
    state_version: int
    simulation_tick: int
    reason: str = ""


class OfflineMatchStore:
    """Test-only atomic store with a single fenced writer and retained fixtures.

    Retention has a fixed record cap; synthetic expiry and network timing are
    intentionally outside this oracle. No record is evicted to admit new work.
    Restart takes an explicit committed snapshot and creates a paused epoch;
    resume is an explicit test action after reconciliation.
    """

    def __init__(self, setup, snapshot, writer_epoch=1):
        validate_setup(setup)
        require(snapshot.game_session_id == setup.game_session_id, "snapshot game session mismatch")
        validate_scalars(snapshot)
        present(snapshot, "match")
        validate_match_state(snapshot.match, setup)
        require(snapshot.tick_duration_us == 5000, "tick duration must remain 5 ms")
        positive(writer_epoch, "writer epoch")
        require(setup.writer_epoch == writer_epoch, "setup writer epoch mismatch")
        self.setup = clone(setup)
        self.snapshot = clone(snapshot)
        self.writer_epoch = writer_epoch
        self.paused = False
        self.queries = {}
        self.commits = {}

    def setup_reply(self, request):
        """Return the retained initial setup ACK; no runtime association install."""
        reply = clone(request)
        reply.response = True
        reply.accepted = False
        if request.game_session_id != self.setup.game_session_id:
            reply.reason = "wrong game session"
        elif request.writer_epoch != self.writer_epoch:
            reply.reason = "writer epoch is fenced"
        elif encoded(request) != encoded(self.setup):
            reply.reason = "setup command or payload differs from retained setup"
        else:
            reply = clone(self.setup)
            reply.response = True
            reply.accepted = True
        return reply

    def query(self, request):
        validate_query(request, self.setup)
        require(not self.paused and request.writer_epoch == self.writer_epoch, "writer is paused or fenced")
        key = request.writer_epoch, request.batch_id
        request_bytes = encoded(request)
        if key in self.queries:
            original, response = self.queries[key]
            require(original == request_bytes, "query identity reused with changed payload")
            return clone(response)
        require(len(self.queries) < 512, "query retention is full; cannot evict unresolved evidence")
        response = pb.BallStateResponse(game_session_id=request.game_session_id,
                                       batch_id=request.batch_id, writer_epoch=request.writer_epoch,
                                       status=pb.QUERY_OK, snapshot=self.snapshot)
        response.queries.extend(request.queries)
        validate_response(response, self.setup, request)
        self.queries[key] = request_bytes, clone(response)
        return response

    def commit(self, update, rejected_keys=()):
        result = lambda status, reason="": CommitResult(
            status, self.snapshot.state_version, self.snapshot.simulation_tick, reason)
        if update.game_session_id != self.setup.game_session_id:
            return result(pb.WRONG_SESSION, "wrong game session")
        if update.writer_epoch != self.writer_epoch:
            return result(pb.WRONG_WRITER, "writer epoch is fenced")
        key = update.writer_epoch, update.batch_id
        payload = encoded(update)
        if key in self.commits:
            original, cached = self.commits[key]
            return cached if original == payload else result(pb.INVALID, "changed duplicate payload")
        if self.paused:
            return result(pb.INVALID, "writer needs explicit reconciliation/resume")
        if key not in self.queries:
            return result(pb.INVALID, "missing required query")
        if len(self.commits) >= 512:
            return result(pb.INVALID, "commit retention is full")
        def retain(status, reason=""):
            terminal = result(status, reason)
            self.commits[key] = payload, terminal
            return terminal
        request_bytes, response = self.queries[key]
        request = pb.BallStateRequest.FromString(request_bytes)
        try:
            validate_update(update, self.setup, request, rejected_keys)
            require(update.base_state_version == response.snapshot.state_version,
                    "candidate does not use its returned query version")
        except ContractError as error:
            return retain(pb.INVALID, str(error))
        if update.base_state_version != self.snapshot.state_version:
            return retain(pb.CONFLICT, "stale base version")
        try:
            require(self.snapshot.simulation_tick <= update.target_simulation_tick <=
                    self.snapshot.simulation_tick + 4, "tick catch-up exceeds four")
            require(all(event.simulation_tick >= self.snapshot.simulation_tick
                        for event in update.rule_events), "rule event predates queried state")
            require(update.match.pi_reference_session_id == self.snapshot.match.pi_reference_session_id
                    and update.match.pi_reference_clock_id == self.snapshot.match.pi_reference_clock_id,
                    "Pi reference cannot change inside a live writer epoch")
            require(update.match.state_time_pi_us >= self.snapshot.match.state_time_pi_us,
                    "Pi state time moves backwards")
            require(update.match.point_id >= self.snapshot.match.point_id,
                    "point identity moves backwards")
            score_changed = encoded(update.match.score) != encoded(self.snapshot.match.score)
            require(not score_changed or any(event.kind in AWARD_EVENTS for event in update.rule_events),
                    "score change lacks an explicit sporting award event")
            require(not any(event.kind == pb.TECHNICAL_PAUSE for event in update.rule_events)
                    or update.match.phase == pb.MATCH_PAUSED, "technical pause requires paused state")
            require(self.snapshot.state_version < MAX_UINT64, "state version exhausted")
        except ContractError as error:
            return retain(pb.INVALID, str(error))
        candidate = clone(self.snapshot)
        candidate.state_version += 1
        candidate.simulation_tick = update.target_simulation_tick
        candidate.match.CopyFrom(update.match)
        self.snapshot = candidate
        return retain(pb.ACCEPTED)

    def restart_writer(self, new_epoch):
        require(self.writer_epoch < new_epoch <= MAX_UINT64, "restart requires a newer bounded epoch")
        self.writer_epoch = new_epoch
        self.paused = True

    def resume_reconciled_writer(self, acknowledged_setup):
        """Accept explicit synthetic setup-ACK evidence for the replacement writer."""
        validate_setup(acknowledged_setup)
        require(acknowledged_setup.response and acknowledged_setup.accepted,
                "replacement writer needs an accepted setup ACK")
        require(acknowledged_setup.writer_epoch == self.writer_epoch,
                "replacement setup uses the wrong epoch")
        require(acknowledged_setup.game_session_id == self.setup.game_session_id and
                acknowledged_setup.configuration_sha256 == self.setup.configuration_sha256,
                "replacement writer must reconcile the same committed configuration")
        self.setup = clone(acknowledged_setup)
        self.setup.response = False
        self.setup.accepted = False
        self.setup.reason = ""
        self.paused = False
