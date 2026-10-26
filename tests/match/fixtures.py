"""Inspectable synthetic candidates, not computed gameplay or hardware data."""

import hashlib


def build_setup(pb):
    setup = pb.MatchSetup(command_id=1, game_session_id=b"G" * 16, writer_epoch=1)
    config = setup.configuration
    config.roster_revision = config.rules_revision = 1
    for slot in range(1, 5):
        config.players.add(player_slot=slot, controller_id=100 + slot,
                           controller_session_id=bytes([slot]) * 16,
                           tracking_session_id=b"T" * 16, person_id=200 + slot,
                           avatar_id=slot, association_version=1, calibration_id=1,
                           right_hand=True, physical_station_id=slot)
    config.rules.CopyFrom(pb.MatchRules(sets_to_win=2, games_to_win_set=6,
                                      minimum_game_lead=2, tiebreak_at_games=6,
                                      tiebreak_points_to_win=7, tiebreak_minimum_lead=2,
                                      final_set_tiebreak=True, tuning_sha256=b"U" * 32))
    setup.configuration_sha256 = hashlib.sha256(
        config.SerializeToString(deterministic=True)).digest()
    return setup


def build_snapshot(pb, setup):
    snapshot = pb.Snapshot(game_session_id=setup.game_session_id, state_version=1,
                           simulation_tick=100, tick_duration_us=5000)
    state = snapshot.match
    state.ball.CopyFrom(pb.Ball(position_m=pb.Vector3(x=1, y=1, z=1),
                               velocity_m_s=pb.Vector3(), radius_m=0.033, calibration_id=1))
    state.roster_revision = setup.configuration.roster_revision
    state.rules_revision = setup.configuration.rules_revision
    state.configuration_sha256 = setup.configuration_sha256
    for slot in range(1, 5):
        state.avatars.add(player_slot=slot, position_m=pb.Vector3(x=slot, z=2),
                          velocity_m_s=pb.Vector3(), target_m=pb.Vector3(x=slot, z=2),
                          movement=pb.HOLDING, coverage_owner_slot=slot)
    state.serve.CopyFrom(pb.ServeState(phase=pb.SERVE_READY, server_slot=1, receiver_slot=3,
                                     side=pb.DEUCE_SIDE, attempt=1,
                                     service_order=[1, 3, 2, 4], receiving_order=[1, 2, 3, 4]))
    state.rally.CopyFrom(pb.RallyState(rally_id=1))
    state.score.CopyFrom(pb.ScoreState())
    state.team_a_near_end = True
    state.phase = pb.MATCH_READY
    state.point_id = 1
    state.state_time_pi_us = 500000
    state.pi_reference_session_id = b"P" * 16
    state.pi_reference_clock_id = 1
    return snapshot


def build_query(pb, setup, periodic=False):
    query = pb.BallStateRequest(game_session_id=setup.game_session_id, writer_epoch=1, batch_id=1)
    if not periodic:
        for index in range(8):
            binding = setup.configuration.players[index // 2]
            query.queries.add(query_id=index + 1,
                              transaction=pb.Transaction(controller_id=binding.controller_id,
                                                         session_id=binding.controller_session_id,
                                                         request_seq=index + 1))
    return query


def build_update(pb, setup, periodic=False):
    update = pb.StateUpdate(game_session_id=setup.game_session_id, writer_epoch=1, batch_id=1,
                            base_state_version=1, target_simulation_tick=101,
                            tracking_session_id=b"T" * 16,
                            match=build_snapshot(pb, setup).match)
    update.match.state_time_pi_us += 5000
    if not periodic:
        query = build_query(pb, setup)
        for index, entry in enumerate(query.queries):
            binding = setup.configuration.players[index // 2]
            update.decisions.add(transaction=entry.transaction, current_sample_id=index + 1,
                                 pose_frame_id=10, person_id=binding.person_id,
                                 association_version=binding.association_version,
                                 imu_capture_us=500000, pose_capture_us=495000,
                                 outcome=pb.MISS, event_index=index, cue=pb.Cue())
    return update
