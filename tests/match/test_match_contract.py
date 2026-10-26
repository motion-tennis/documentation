"""Known-answer/rejection fixtures for the offline full-match contract only."""

import hashlib
import unittest

import motion_pb2 as pb
from fixtures import build_query, build_setup, build_snapshot, build_update
from match_contract import (ContractError, MAX_UINT64, OfflineMatchStore, clone,
                            configuration_hash, encoded, transaction_key,
                            validate_match_state, validate_query, validate_response, validate_setup,
                            validate_update)


class MatchContractTests(unittest.TestCase):
    def setUp(self):
        self.setup = build_setup(pb)
        self.snapshot = build_snapshot(pb, self.setup)
        self.query = build_query(pb, self.setup)
        self.update = build_update(pb, self.setup)
        self.store = OfflineMatchStore(self.setup, self.snapshot)

    def rehash(self, setup):
        setup.configuration_sha256 = hashlib.sha256(encoded(setup.configuration)).digest()

    def test_complete_eight_input_batch_and_snapshot(self):
        validate_setup(self.setup)
        validate_match_state(self.snapshot.match, self.setup)
        response = self.store.query(self.query)
        self.assertEqual(encoded(response.snapshot), encoded(self.snapshot))
        self.assertEqual([encoded(q) for q in response.queries], [encoded(q) for q in self.query.queries])
        result = self.store.commit(self.update)
        self.assertEqual((result.status, result.state_version, result.simulation_tick), (pb.ACCEPTED, 2, 101))
        self.assertEqual(encoded(self.store.snapshot.match), encoded(self.update.match))
        self.assertEqual(len(self.update.decisions), 8)

    def test_setup_hash_is_stable_and_complete(self):
        self.assertEqual(configuration_hash(self.setup.configuration), self.setup.configuration_sha256)
        changed = clone(self.setup)
        changed.configuration.players[0].right_hand = False
        with self.assertRaisesRegex(ContractError, "hash mismatch"):
            validate_setup(changed)

    def test_configuration_unknown_fields_are_rejected_before_hashing(self):
        unknown = pb.MatchConfiguration.FromString(encoded(self.setup.configuration) + b"\xa0\x06\x01")
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            configuration_hash(unknown)

    def test_setup_uniqueness_order_and_revision_rejections(self):
        mutations = {
            "duplicate slot": lambda c: setattr(c.players[1], "player_slot", 1),
            "duplicate controller": lambda c: setattr(c.players[1], "controller_id", 101),
            "duplicate person": lambda c: setattr(c.players[1], "person_id", 201),
            "duplicate avatar": lambda c: setattr(c.players[0], "avatar_id", 2),
            "short session": lambda c: setattr(c.players[0], "controller_session_id", b"short"),
            "mixed tracker": lambda c: setattr(c.players[0], "tracking_session_id", b"Z" * 16),
            "missing revision": lambda c: setattr(c, "roster_revision", 0),
            "too many sets": lambda c: setattr(c.rules, "sets_to_win", 4),
            "missing tuning": lambda c: setattr(c.rules, "tuning_sha256", b""),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                setup = clone(self.setup)
                mutate(setup.configuration)
                self.rehash(setup)
                with self.assertRaises(ContractError):
                    validate_setup(setup)

    def test_setup_ack_retries_and_epoch_fencing(self):
        first = self.store.setup_reply(self.setup)
        self.assertTrue(first.response and first.accepted)
        self.assertEqual(encoded(first), encoded(self.store.setup_reply(self.setup)))
        changed = clone(self.setup)
        changed.configuration.players[0].right_hand = False
        self.rehash(changed)
        self.assertFalse(self.store.setup_reply(changed).accepted)
        changed = clone(self.setup)
        changed.writer_epoch = 2
        self.assertFalse(self.store.setup_reply(changed).accepted)
        with self.assertRaisesRegex(ContractError, "epoch mismatch"):
            OfflineMatchStore(changed, self.snapshot)

    def test_state_missing_fields_bounds_and_provenance(self):
        mutations = {
            "missing ball": lambda s: s.ClearField("ball"),
            "missing position": lambda s: s.ball.ClearField("position_m"),
            "missing score": lambda s: s.ClearField("score"),
            "wrong revision": lambda s: setattr(s, "roster_revision", 2),
            "wrong hash": lambda s: setattr(s, "configuration_sha256", b"X" * 32),
            "missing avatar": lambda s: s.avatars.pop(),
            "nonfinite": lambda s: setattr(s.ball.position_m, "x", float("nan")),
            "invalid enum": lambda s: setattr(s, "phase", 999),
            "oversized time": lambda s: setattr(s, "state_time_pi_us", MAX_UINT64 + 1),
            "short Pi session": lambda s: setattr(s, "pi_reference_session_id", b"P"),
            "wrong teammate": lambda s: setattr(s.avatars[0], "coverage_owner_slot", 3),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                state = clone(self.snapshot.match)
                mutate(state)
                with self.assertRaises(ContractError):
                    validate_match_state(state, self.setup)

    def test_serve_orders_and_attempts(self):
        for field, value in (("attempt", 3), ("server_slot", 2), ("receiver_slot", 1),
                             ("service_turn_index", 4), ("side", pb.SERVICE_UNSPECIFIED)):
            with self.subTest(field=field):
                state = clone(self.snapshot.match)
                setattr(state.serve, field, value)
                with self.assertRaises(ContractError):
                    validate_match_state(state, self.setup)
        state = clone(self.snapshot.match)
        state.serve.service_order[:] = [1, 2, 3, 4]
        with self.assertRaisesRegex(ContractError, "alternate"):
            validate_match_state(state, self.setup)

    def test_cancelled_toss_and_let_preserve_attempt_as_prepared_candidates(self):
        for event_kind, phase, attempted in ((pb.TOSS_CANCELLED, pb.SERVE_READY, False),
                                             (pb.SERVE_LET_EVENT, pb.SERVE_LET, True)):
            with self.subTest(event=event_kind):
                query = build_query(pb, self.setup, periodic=True)
                update = build_update(pb, self.setup, periodic=True)
                update.match.serve.attempt = 2
                update.match.serve.phase = phase
                update.match.serve.stroke_attempted = attempted
                update.rule_events.add(event_index=8, kind=event_kind, point_id=1,
                                       player_slot=1, serve_attempt=2, simulation_tick=101)
                validate_update(update, self.setup, query)
                self.assertEqual(update.match.serve.attempt, 2)

    def test_score_deuce_advantage_tiebreak_and_completed_sets(self):
        state = clone(self.snapshot.match)
        state.score.points_a = pb.ADVANTAGE
        state.score.points_b = pb.FORTY
        validate_match_state(state, self.setup)
        state.score.points_b = pb.THIRTY
        with self.assertRaises(ContractError):
            validate_match_state(state, self.setup)
        state.score.CopyFrom(pb.ScoreState(tiebreak=True, games_a=6, games_b=6,
                                           tiebreak_points_a=8, tiebreak_points_b=8))
        state.serve.tiebreak_first_server_slot = 1
        validate_match_state(state, self.setup)
        state.score.CopyFrom(pb.ScoreState(sets_a=1))
        state.score.completed_sets.add(games_a=7, games_b=6, had_tiebreak=True,
                                       tiebreak_points_a=10, tiebreak_points_b=8)
        validate_match_state(state, self.setup)
        state.score.completed_sets[0].tiebreak_points_a = 9
        with self.assertRaises(ContractError):
            validate_match_state(state, self.setup)

    def test_match_winner_and_set_totals_must_agree(self):
        state = clone(self.snapshot.match)
        state.score.sets_a = 2
        state.score.completed_sets.add(games_a=6, games_b=0)
        state.score.completed_sets.add(games_a=6, games_b=4)
        state.phase = pb.MATCH_FINISHED
        state.winner = pb.TEAM_A
        validate_match_state(state, self.setup)
        state.winner = pb.TEAM_B
        with self.assertRaises(ContractError):
            validate_match_state(state, self.setup)

    def test_query_limits_and_distinct_identity(self):
        query = clone(self.query)
        query.queries.add().CopyFrom(query.queries[0])
        with self.assertRaisesRegex(ContractError, "eight"):
            validate_query(query, self.setup)
        query = clone(self.query)
        query.queries[2].transaction.controller_id = 101
        query.queries[2].transaction.session_id = bytes([1]) * 16
        with self.assertRaisesRegex(ContractError, "two queries"):
            validate_query(query, self.setup)
        query = clone(self.query)
        query.queries[1].query_id = query.queries[0].query_id
        with self.assertRaisesRegex(ContractError, "duplicate"):
            validate_query(query, self.setup)

    def test_source_order_exactly_matches_decisions(self):
        changed = clone(self.update)
        first = clone(changed.decisions[0])
        changed.decisions[0].CopyFrom(changed.decisions[1])
        changed.decisions[1].CopyFrom(first)
        with self.assertRaisesRegex(ContractError, "source query order"):
            validate_update(changed, self.setup, self.query)
        changed = clone(self.update)
        changed.decisions.pop()
        with self.assertRaisesRegex(ContractError, "source query order"):
            validate_update(changed, self.setup, self.query)

    def test_query_responses_bind_session_epoch_batch_and_echoes_on_rejection(self):
        response = self.store.query(self.query)
        for field, value in (("game_session_id", b"X" * 16), ("writer_epoch", 2), ("batch_id", 2)):
            changed = clone(response)
            setattr(changed, field, value)
            with self.assertRaisesRegex(ContractError, "identity mismatch"):
                validate_response(changed, self.setup, self.query)
        changed = clone(response)
        changed.snapshot.game_session_id = b"X" * 16
        with self.assertRaisesRegex(ContractError, "snapshot game session"):
            validate_response(changed, self.setup, self.query)
        rejected = clone(response)
        rejected.status = pb.QUERY_REJECTED
        rejected.reason = "writer paused"
        rejected.ClearField("snapshot")
        validate_response(rejected, self.setup, self.query)
        rejected.ClearField("game_session_id")
        with self.assertRaisesRegex(ContractError, "identity mismatch"):
            validate_response(rejected, self.setup, self.query)

    def test_embedded_nul_is_rejected_for_static_c_strings(self):
        setup = clone(self.setup)
        setup.reason = "visible\x00hidden"
        with self.assertRaisesRegex(ContractError, "embedded NUL"):
            validate_setup(setup)

    def test_avatar_identifiers_are_distinct_from_slot_numbers(self):
        setup = clone(self.setup)
        for player in setup.configuration.players:
            player.avatar_id += 1000
        self.rehash(setup)
        validate_setup(setup)

    def test_invalid_input_removal_is_explicit_and_remaining_order_is_preserved(self):
        changed = clone(self.update)
        rejected = transaction_key(changed.decisions[0].transaction)
        del changed.decisions[0]
        for index, decision in enumerate(changed.decisions):
            decision.event_index = index
        validate_update(changed, self.setup, self.query, rejected_keys=[rejected])
        with self.assertRaises(ContractError):
            validate_update(changed, self.setup, self.query)
        self.store.query(self.query)
        self.assertEqual(self.store.commit(changed, rejected_keys=[rejected]).status, pb.ACCEPTED)

    def test_decision_semantics_and_rule_event_bounds(self):
        mutations = {
            "error outcome": lambda u: setattr(u.decisions[0], "outcome", pb.TRACKING_UNAVAILABLE),
            "wrong person": lambda u: setattr(u.decisions[0], "person_id", 999),
            "stale association": lambda u: setattr(u.decisions[0], "association_version", 2),
            "wrong tracker": lambda u: setattr(u, "tracking_session_id", b"Z" * 16),
            "duplicate index": lambda u: setattr(u.decisions[1], "event_index", 0),
            "missing cue": lambda u: u.decisions[0].ClearField("cue"),
            "invalid intensity": lambda u: setattr(u.decisions[0].cue, "intensity", 1.1),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                update = clone(self.update)
                mutate(update)
                with self.assertRaises(ContractError):
                    validate_update(update, self.setup, self.query)
        update = clone(self.update)
        update.rule_events.add(event_index=0, kind=pb.BALL_BOUNCE, point_id=1, simulation_tick=101)
        with self.assertRaisesRegex(ContractError, "from eight"):
            validate_update(update, self.setup, self.query)

    def test_periodic_only_award_has_no_invented_transaction(self):
        query = build_query(pb, self.setup, periodic=True)
        update = build_update(pb, self.setup, periodic=True)
        update.match.score.points_a = pb.FIFTEEN
        update.rule_events.add(event_index=8, kind=pb.POINT_AWARDED, point_id=1,
                               team=pb.TEAM_A, simulation_tick=101)
        self.store.query(query)
        self.assertEqual(self.store.commit(update).status, pb.ACCEPTED)
        self.assertEqual(len(update.decisions), 0)
        update.rule_events[0].has_cause = True
        with self.assertRaisesRegex(ContractError, "missing event cause"):
            validate_update(update, self.setup, query)

    def test_sample_misses_do_not_compute_or_award_points(self):
        self.store.query(self.query)
        self.assertTrue(all(d.outcome == pb.MISS for d in self.update.decisions))
        self.assertEqual(self.store.commit(self.update).status, pb.ACCEPTED)
        self.assertEqual(encoded(self.store.snapshot.match.score), encoded(self.snapshot.match.score))
        store = OfflineMatchStore(self.setup, self.snapshot)
        store.query(self.query)
        self.update.match.score.points_b = pb.FIFTEEN
        self.assertEqual(store.commit(self.update).status, pb.INVALID)
        self.assertEqual(encoded(store.snapshot), encoded(self.snapshot))

    def test_technical_pause_preserves_score(self):
        self.store.query(self.query)
        self.update.match.phase = pb.MATCH_PAUSED
        self.update.rule_events.add(event_index=8, kind=pb.TECHNICAL_PAUSE, point_id=1,
                                    simulation_tick=101)
        self.assertEqual(self.store.commit(self.update).status, pb.ACCEPTED)
        self.assertEqual(encoded(self.store.snapshot.match.score), encoded(self.snapshot.match.score))
        self.update.rule_events[0].team = pb.TEAM_B
        with self.assertRaises(ContractError):
            validate_update(self.update, self.setup, self.query)

    def test_end_change_keeps_roster_and_avatar_identity(self):
        self.store.query(self.query)
        self.update.match.team_a_near_end = False
        self.update.rule_events.add(event_index=8, kind=pb.ENDS_CHANGED, point_id=1,
                                    simulation_tick=101)
        self.assertEqual(self.store.commit(self.update).status, pb.ACCEPTED)
        self.assertEqual(self.store.snapshot.match.roster_revision, 1)
        self.assertEqual([a.player_slot for a in self.store.snapshot.match.avatars], [1, 2, 3, 4])

    def test_duplicate_commit_returns_original_version_without_reapplying(self):
        self.store.query(self.query)
        accepted = self.store.commit(self.update)
        self.assertEqual(self.store.commit(self.update), accepted)
        self.assertEqual(self.store.snapshot.state_version, 2)
        changed = clone(self.update)
        changed.match.ball.position_m.x += 1
        self.assertEqual(self.store.commit(changed).status, pb.INVALID)
        self.assertEqual(self.store.snapshot.state_version, 2)

    def test_rejected_commit_retry_keeps_original_result_after_other_commit(self):
        self.store.query(self.query)
        invalid = clone(self.update)
        invalid.match.score.points_a = pb.FIFTEEN
        rejected = self.store.commit(invalid)
        self.assertEqual(rejected.status, pb.INVALID)
        query = clone(self.query)
        query.batch_id = 2
        self.store.query(query)
        update = clone(self.update)
        update.batch_id = 2
        self.assertEqual(self.store.commit(update).status, pb.ACCEPTED)
        self.assertEqual(self.store.commit(invalid), rejected)
        self.assertEqual(rejected.state_version, 1)
        changed = clone(self.update)
        changed.match.ball.position_m.x += 1
        self.assertEqual(self.store.commit(changed).status, pb.INVALID)
        self.assertEqual(self.store.snapshot.state_version, 2)

    def test_query_retry_returns_original_snapshot_after_later_commit(self):
        response = self.store.query(self.query)
        self.store.commit(self.update)
        self.assertEqual(encoded(self.store.query(self.query)), encoded(response))
        changed = clone(self.query)
        changed.queries[0].query_id += 100
        with self.assertRaisesRegex(ContractError, "changed payload"):
            self.store.query(changed)

    def test_stale_query_candidate_conflicts_atomically(self):
        second_query = clone(self.query)
        second_query.batch_id = 2
        self.store.query(self.query)
        self.store.query(second_query)
        self.store.commit(self.update)
        before = encoded(self.store.snapshot)
        stale = clone(self.update)
        stale.batch_id = 2
        stale.match.ball.position_m.x = 123
        stale.match.avatars[0].position_m.x = 456
        self.assertEqual(self.store.commit(stale).status, pb.CONFLICT)
        self.assertEqual(encoded(self.store.snapshot), before)

    def test_wrong_session_epoch_and_missing_query_do_not_mutate(self):
        for field, value, expected in (("game_session_id", b"X" * 16, pb.WRONG_SESSION),
                                       ("writer_epoch", 2, pb.WRONG_WRITER),
                                       ("batch_id", 2, pb.INVALID)):
            with self.subTest(field=field):
                update = clone(self.update)
                setattr(update, field, value)
                self.assertEqual(self.store.commit(update).status, expected)
                self.assertEqual(encoded(self.store.snapshot), encoded(self.snapshot))

    def test_rejected_candidate_rolls_back_complete_visible_match(self):
        self.store.query(self.query)
        self.update.match.ball.position_m.x = 10
        self.update.match.avatars[0].position_m.x = 20
        self.update.match.serve.attempt = 2
        self.update.match.rally.contact_slot_mask = 1
        self.update.match.score.points_a = pb.FIFTEEN
        self.assertEqual(self.store.commit(self.update).status, pb.INVALID)
        self.assertEqual(encoded(self.store.snapshot), encoded(self.snapshot))

    def test_point_identity_regression_preserves_entire_snapshot(self):
        snapshot = clone(self.snapshot)
        snapshot.match.point_id = 2
        store = OfflineMatchStore(self.setup, snapshot)
        store.query(self.query)
        update = clone(self.update)
        update.match.point_id = 1
        update.match.ball.position_m.x = 10
        update.match.avatars[0].position_m.x = 20
        update.match.serve.attempt = 2
        update.match.rally.contact_slot_mask = 1
        result = store.commit(update)
        self.assertEqual(result.status, pb.INVALID)
        self.assertIn("point identity moves backwards", result.reason)
        self.assertEqual(encoded(store.snapshot), encoded(snapshot))

    def test_restart_fences_old_writer_and_requires_explicit_resume(self):
        self.store.query(self.query)
        self.store.restart_writer(2)
        self.assertEqual(self.store.commit(self.update).status, pb.WRONG_WRITER)
        query = clone(self.query)
        query.writer_epoch = 2
        with self.assertRaisesRegex(ContractError, "paused"):
            self.store.query(query)
        with self.assertRaises(ContractError):
            self.store.resume_reconciled_writer(self.setup)
        acknowledged_setup = clone(self.setup)
        acknowledged_setup.command_id = 2
        acknowledged_setup.writer_epoch = 2
        acknowledged_setup.response = acknowledged_setup.accepted = True
        self.store.resume_reconciled_writer(acknowledged_setup)
        self.store.query(query)
        update = clone(self.update)
        update.writer_epoch = 2
        self.assertEqual(self.store.commit(update).status, pb.ACCEPTED)

    def test_new_game_session_rejects_previous_game_payload(self):
        setup = clone(self.setup)
        setup.game_session_id = b"N" * 16
        fresh = OfflineMatchStore(setup, build_snapshot(pb, setup))
        self.assertEqual(fresh.commit(self.update).status, pb.WRONG_SESSION)
        self.assertEqual(fresh.snapshot.state_version, 1)

    def test_tick_reference_and_time_guards(self):
        self.store.query(self.query)
        for field, value in (("state_time_pi_us", 1), ("pi_reference_session_id", b"X" * 16)):
            update = clone(self.update)
            setattr(update.match, field, value)
            self.assertEqual(self.store.commit(update).status, pb.INVALID)
        update = clone(self.update)
        update.target_simulation_tick = 105
        self.assertEqual(self.store.commit(update).status, pb.INVALID)

    def test_retention_pressure_rejects_without_evicting_query_evidence(self):
        for batch in range(1, 513):
            query = clone(self.query)
            query.batch_id = batch
            self.store.query(query)
        original = self.store.query(self.query)
        query.batch_id = 513
        with self.assertRaisesRegex(ContractError, "retention is full"):
            self.store.query(query)
        self.assertEqual(encoded(self.store.query(self.query)), encoded(original))


if __name__ == "__main__":
    unittest.main()
