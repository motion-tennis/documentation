"""Bounded generated-codec cases invoked by scripts/contract/check_contract.py."""

import hashlib

from wire_bounds import collection_bounds, fill_maximum, validate_envelope, validate_fields


def envelope(module):
    return module.Envelope(major=0, minor=3, sender_id=1,
                           sender_session_id=b"s" * 16, message_seq=1,
                           sent_time_us=1000000, clock_id=1, run_id=b"r" * 16)


def expect_rejection(results, name, function):
    try:
        function()
    except ValueError:
        results.append({"name": name, "rejected_by": "contract_field_validator"})
    else:
        raise AssertionError(f"Expected rejection: {name}")


def high_width_fixture(module, build_setup, build_query, build_update):
    """Admitted field/correlation fixture, not a calculated or measured rally."""
    setup = build_setup(module)
    maximum = (1 << 56) - 1
    for index, player in enumerate(setup.configuration.players):
        player.controller_id = (1 << 32) - 1 - index
        player.person_id = (1 << 32) - 1 - index
        player.association_version = (1 << 32) - 1
    setup.configuration.roster_revision = (1 << 32) - 1
    setup.configuration.rules_revision = (1 << 32) - 1
    setup.configuration_sha256 = hashlib.sha256(
        setup.configuration.SerializeToString(deterministic=True)).digest()
    query = build_query(module, setup)
    update = build_update(module, setup)
    query.batch_id = update.batch_id = maximum - 100
    for index, (entry, decision) in enumerate(zip(query.queries, update.decisions)):
        entry.query_id = maximum - index
        entry.transaction.request_seq = maximum - index
        decision.transaction.CopyFrom(entry.transaction)
        decision.current_sample_id = maximum - index
        decision.pose_frame_id = maximum - index
        decision.imu_capture_us = maximum - 10000
        decision.pose_capture_us = maximum - 15000
        decision.outcome = module.HIT
        decision.swing_id = maximum - index
        decision.cue.CopyFrom(module.Cue(kind=module.CUE_HIT, cue_id=maximum - index,
                                        intensity=1.0, duration_ms=20, electrical_eligible=True))
    update.match.state_time_pi_us = maximum - 5000
    update.match.ball.velocity_m_s.CopyFrom(module.Vector3(x=1, y=1, z=1))
    for avatar in update.match.avatars:
        avatar.velocity_m_s.CopyFrom(module.Vector3(x=1, y=1, z=1))
        avatar.heading_rad = 0.5
    return setup, query, update


def run_generated_checks(module, profile, codec):
    results = []
    paths = {
        "SkeletonFrame.joints": "skeleton_frame.joints",
        "FrameStatus.person_ids": "frame_status.person_ids",
        "BallStateRequest.queries": "ball_state_request.queries",
        "BallStateResponse.queries": "ball_state_response.queries",
        "StateUpdate.decisions": "state_update.decisions",
        "StatePublication.decisions": "state_publication.decisions",
        "StateUpdate.rule_events": "state_update.rule_events",
        "StatePublication.rule_events": "state_publication.rule_events",
        "MatchConfiguration.players": "match_setup.configuration.players",
        "MatchState.avatars": "state_update.match.avatars",
        "ServeState.service_order": "state_update.match.serve.service_order",
        "ServeState.receiving_order": "state_update.match.serve.receiving_order",
        "ScoreState.completed_sets": "state_update.match.score.completed_sets",
    }
    bounds = collection_bounds(profile)
    if set(paths) != set(bounds):
        raise AssertionError("Missing collection-overflow fixture")
    for key, path in paths.items():
        candidate = envelope(module)
        fields = path.split(".")
        container = candidate
        for field in fields:
            container = getattr(container, field)
        for _ in range(bounds[key] + 1):
            if hasattr(container, "add"):
                container.add()
            else:
                container.append(1)
        results.append(codec.reject_c("overflow_" + key, candidate.SerializeToString()))
        expect_rejection(results, "field_bound_" + key,
                         lambda candidate=candidate: validate_fields(candidate, profile))

    variable_cases = [
        ("uuid", "sender_session_id", b"x" * 17),
        ("sha256", "hello.schema_sha256", b"x" * 33),
        ("reason_utf8", "hello_result.reason", "\u00e9" * (profile["limits"]["reason_utf8_bytes"] // 2 + 1)),
        ("role", "hello.role", "x" * (profile["limits"]["role_utf8_bytes"] + 1)),
        ("operation", "control_command.operation", "x" * 17),
        ("configuration", "control_command.configuration_json_utf8", b"x" * (profile["limits"]["configuration_json_bytes"] + 1)),
    ]
    for name, path, value in variable_cases:
        candidate = envelope(module)
        destination = candidate
        fields = path.split(".")
        for field in fields[:-1]:
            destination = getattr(destination, field)
        setattr(destination, fields[-1], value)
        results.append(codec.reject_c("overflow_" + name, candidate.SerializeToString()))
        expect_rejection(results, "field_bound_" + name,
                         lambda candidate=candidate: validate_fields(candidate, profile))

    good = envelope(module)
    good.controller_input.transaction.controller_id = 1
    good.controller_input.transaction.session_id = good.sender_session_id
    good.controller_input.transaction.request_seq = 1
    good.controller_input.t0_us = 1000000
    good.controller_input.sample_id = 1
    good.controller_input.capture.value_us = 1000000
    good.controller_input.capture.clock_id = 1
    good.controller_input.capture.kind = module.IRQ_MONOTONIC
    good.controller_input.capture.timing_valid = True
    good.controller_input.association_version = 1
    good.controller_input.calibration_id = 1
    good.controller_input.specific_force_m_s2.y = 9.81
    good.controller_input.angular_velocity_rad_s.x = 0.25
    good.controller_input.battery_millivolts = 3700
    validate_envelope(good, profile, "udp")
    codec.roundtrip("controller_regular_sample", good)
    good.controller_input.transaction.session_id = b"c" * 16
    expect_rejection(results, "controller_sender_session_mismatch", lambda: validate_envelope(good, profile))
    good.controller_input.transaction.session_id = good.sender_session_id
    good.controller_input.transaction.controller_id = 2
    expect_rejection(results, "controller_sender_id_mismatch", lambda: validate_envelope(good, profile))
    good.controller_input.transaction.controller_id = 1
    no_capture = module.Envelope()
    no_capture.CopyFrom(good)
    no_capture.controller_input.ClearField("capture")
    expect_rejection(results, "missing_controller_capture", lambda: validate_envelope(no_capture, profile))

    skeleton = envelope(module)
    skeleton.skeleton_frame.frame_id = 1
    skeleton.skeleton_frame.person_id = 1
    skeleton.skeleton_frame.capture.CopyFrom(good.controller_input.capture)
    skeleton.skeleton_frame.capture.kind = module.DRIVER_FRAME
    skeleton.skeleton_frame.processing_complete_us = 1001000
    skeleton.skeleton_frame.processing_clock_id = 1
    skeleton.skeleton_frame.image_width = 1920
    skeleton.skeleton_frame.image_height = 1080
    skeleton.skeleton_frame.calibration_id = 1
    skeleton.skeleton_frame.state = module.TRACKED
    for index in range(17):
        skeleton.skeleton_frame.joints.add(coco_joint_index=index, x_normalized=0.5,
                                          y_normalized=0.5, score=0.9, state=module.TRACKED)
    validate_envelope(skeleton, profile, "udp")
    codec.roundtrip("seventeen_joint_pose", skeleton)
    skeleton.skeleton_frame.joints[16].coco_joint_index = 0
    expect_rejection(results, "duplicate_coco_joint", lambda: validate_envelope(skeleton, profile))
    skeleton.skeleton_frame.joints[16].coco_joint_index = 16
    skeleton.skeleton_frame.joints[0].x_normalized = 1.5
    expect_rejection(results, "out_of_frame_tracked_joint", lambda: validate_envelope(skeleton, profile))
    skeleton.skeleton_frame.joints[0].x_normalized = 0.5
    skeleton.skeleton_frame.joints[0].state = module.TRACKING_UNSPECIFIED
    expect_rejection(results, "unspecified_joint_state", lambda: validate_envelope(skeleton, profile))
    frame_status = envelope(module)
    frame_status.frame_status.person_ids.extend([1, 1])
    expect_rejection(results, "duplicate_frame_person", lambda: validate_envelope(frame_status, profile))

    maximum = int(profile["limits"]["maximum_wire_uint64"])
    good.message_seq = maximum
    validate_envelope(good, profile)
    codec.roundtrip("maximum_legal_uint64", good)
    good.message_seq = maximum + 1
    expect_rejection(results, "uint64_profile_overflow", lambda: validate_envelope(good, profile))
    good.message_seq = 1
    good.controller_input.specific_force_m_s2.x = float("nan")
    expect_rejection(results, "nan_physical_value", lambda: validate_envelope(good, profile))
    good.controller_input.specific_force_m_s2.x = float("inf")
    expect_rejection(results, "infinite_physical_value", lambda: validate_envelope(good, profile))
    good.controller_input.specific_force_m_s2.x = 0
    good.controller_input.capture.kind = 127
    expect_rejection(results, "unknown_enum", lambda: validate_envelope(good, profile))
    good.controller_input.capture.kind = module.IRQ_MONOTONIC
    nul_string = envelope(module)
    nul_string.hello_result.reason = "bad\x00reason"
    expect_rejection(results, "embedded_nul_string", lambda: validate_envelope(nul_string, profile))
    results.append(codec.reject_c("embedded_nul_wire_string", nul_string.SerializeToString()))
    good.minor = 2
    expect_rejection(results, "legacy_protocol_version", lambda: validate_envelope(good, profile))
    good.minor = 3
    good.sender_session_id = b"x" * 15
    expect_rejection(results, "short_envelope_uuid", lambda: validate_envelope(good, profile))
    good.sender_session_id = b"s" * 16
    expect_rejection(results, "wrong_message_transport", lambda: validate_envelope(good, profile, "state_tcp"))
    unknown = module.Envelope.FromString(good.SerializeToString() + b"\xb8\x3e\x01")
    expect_rejection(results, "unknown_wire_field", lambda: validate_envelope(unknown, profile))
    results.append(codec.reject_c("unknown_wire_field", unknown.SerializeToString()))
    results.append(codec.reject_c("duplicate_wire_field", good.SerializeToString() + b"\x10\x03"))
    absent = envelope(module)
    expect_rejection(results, "missing_body", lambda: validate_envelope(absent, profile))
    absent.sender_id = 0
    expect_rejection(results, "missing_sender_identity", lambda: validate_envelope(absent, profile))

    maximal = fill_maximum(module.Envelope(), profile)
    fill_maximum(maximal.controller_input, profile)
    results.append(codec.reject_c("truncated_protobuf", maximal.SerializeToString()[:-1]))
    results.append(codec.reject_c("unterminated_varint", b"\x80" * 11))
    results.append(codec.reject_c("invalid_utf8_role", b"\xc2\x02\x03\x0a\x01\xff"))
    return results
