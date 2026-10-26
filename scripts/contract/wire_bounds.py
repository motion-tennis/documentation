"""Descriptor-driven static limits for the proposed v0.3 validation fixtures."""

import math

from google.protobuf.descriptor import FieldDescriptor as Field


def field_key(field):
    return f"{field.containing_type.name}.{field.name}"


def collection_bounds(profile):
    limits = profile["limits"]
    players = profile["players"]
    return {
        "SkeletonFrame.joints": 17,
        "FrameStatus.person_ids": players,
        "BallStateRequest.queries": limits["batch_transactions"],
        "BallStateResponse.queries": limits["batch_transactions"],
        "StateUpdate.decisions": limits["batch_transactions"],
        "StatePublication.decisions": limits["batch_transactions"],
        "StateUpdate.rule_events": limits["rule_events_per_batch"],
        "StatePublication.rule_events": limits["rule_events_per_batch"],
        "MatchConfiguration.players": players,
        "MatchState.avatars": players,
        "ServeState.service_order": players,
        "ServeState.receiving_order": players,
        "ScoreState.completed_sets": limits["completed_sets"],
    }


def variable_bound(field, profile):
    limits = profile["limits"]
    if field.type == Field.TYPE_BYTES:
        if field.name == "configuration_json_utf8":
            return limits["configuration_json_bytes"]
        if field.name.endswith("sha256"):
            return 32
        if field.name.endswith("session_id") or field.name == "run_id":
            return 16
    elif field.type == Field.TYPE_STRING:
        if field.name == "reason":
            return limits["reason_utf8_bytes"]
        if field.name == "role":
            return limits["role_utf8_bytes"]
        if field.name == "operation":
            return 16
    raise ValueError(f"No explicit variable-field bound for {field.full_name}")


def nanopb_options(module, profile):
    lines = ["// Generated from the profile by check_contract.py; validation only.", "* type:FT_STATIC"]
    collections = collection_bounds(profile)
    used = set()
    for descriptor in module.DESCRIPTOR.message_types_by_name.values():
        for field in descriptor.fields:
            options = []
            if field.is_repeated:
                key = field_key(field)
                options.append(f"max_count:{collections[key]}")
                used.add(key)
            if field.type in (Field.TYPE_BYTES, Field.TYPE_STRING):
                option = "max_length" if field.type == Field.TYPE_STRING else "max_size"
                options.append(f"{option}:{variable_bound(field, profile)}")
            if options:
                lines.append(f"{field.full_name} {' '.join(options)}")
    if used != set(collections):
        raise ValueError(f"Stale collection bounds: {sorted(set(collections) - used)}")
    return "\n".join(lines) + "\n"


def maximum_scalar(field, profile):
    if field.type == Field.TYPE_UINT64:
        return int(profile["limits"]["maximum_wire_uint64"])
    if field.type == Field.TYPE_UINT32:
        return 2**32 - 1
    if field.type == Field.TYPE_BOOL:
        return True
    if field.type in (Field.TYPE_FLOAT, Field.TYPE_DOUBLE):
        return 1.5
    if field.type == Field.TYPE_ENUM:
        return max(value.number for value in field.enum_type.values)
    if field.type == Field.TYPE_STRING:
        return "x" * variable_bound(field, profile)
    if field.type == Field.TYPE_BYTES:
        return b"x" * variable_bound(field, profile)
    raise ValueError(f"Unsupported scalar type: {field.full_name}")


def fill_maximum(message, profile, *, collections=None):
    """Construct a conservative size witness, not a semantically valid match."""
    collections = collection_bounds(profile) if collections is None else collections
    for field in message.DESCRIPTOR.fields:
        if field.containing_oneof:
            continue
        if field.is_repeated:
            destination = getattr(message, field.name)
            count = collections[field_key(field)]
            for _ in range(count):
                if field.type == Field.TYPE_MESSAGE:
                    fill_maximum(destination.add(), profile, collections=collections)
                else:
                    destination.append(maximum_scalar(field, profile))
        elif field.type == Field.TYPE_MESSAGE:
            fill_maximum(getattr(message, field.name), profile, collections=collections)
        else:
            setattr(message, field.name, maximum_scalar(field, profile))
    return message


def validate_fields(message, profile):
    """Check all encoded fields independently of the full-match semantic oracle."""
    collections = collection_bounds(profile)
    maximum_uint64 = int(profile["limits"]["maximum_wire_uint64"])
    for field, value in message.ListFields():
        if field.is_repeated and len(value) > collections[field_key(field)]:
            raise ValueError(f"Collection limit exceeded: {field.full_name}")
        values = value if field.is_repeated else [value]
        for item in values:
            if field.type == Field.TYPE_MESSAGE:
                validate_fields(item, profile)
            elif field.type == Field.TYPE_UINT64 and item > maximum_uint64:
                raise ValueError(f"uint64 profile limit exceeded: {field.full_name}")
            elif field.type in (Field.TYPE_FLOAT, Field.TYPE_DOUBLE) and not math.isfinite(item):
                raise ValueError(f"Non-finite physical value: {field.full_name}")
            elif field.type == Field.TYPE_ENUM and item not in field.enum_type.values_by_number:
                raise ValueError(f"Unknown enum value: {field.full_name}")
            elif field.type in (Field.TYPE_BYTES, Field.TYPE_STRING):
                if field.type == Field.TYPE_STRING and "\x00" in item:
                    raise ValueError(f"Embedded NUL in bounded C string: {field.full_name}")
                encoded = item.encode("utf-8") if isinstance(item, str) else item
                if len(encoded) > variable_bound(field, profile):
                    raise ValueError(f"Variable-field limit exceeded: {field.full_name}")


def body_transports(body, profile):
    choices = {
        "udp_bodies": ("udp", profile["limits"]["udp_payload_bytes"]),
        "state_stream_bodies": ("state_tcp", profile["limits"]["state_stream_frame_bytes"]),
        "publication_stream_bodies": ("publication_tcp", profile["limits"]["state_stream_frame_bytes"]),
        "control_stream_bodies": ("control_tcp", profile["limits"]["maximum_stream_frame_bytes"]),
    }
    matches = [choices[key] for key in choices if body in profile["transport"][key]]
    if not matches:
        raise ValueError(f"No allowed transport for {body}")
    return matches


def body_transport(body, profile):
    """The strictest allowed cap is sufficient for the encoded-size proof."""
    matches = body_transports(body, profile)
    return "/".join(transport for transport, _ in matches), min(cap for _, cap in matches)


def validate_envelope(envelope, profile, transport=None):
    if (envelope.major, envelope.minor) != (0, 3):
        raise ValueError("Unsupported protocol version")
    if not envelope.sender_id or not envelope.clock_id or not envelope.message_seq:
        raise ValueError("Missing sender, clock or message identity")
    if len(envelope.sender_session_id) != 16 or len(envelope.run_id) != 16:
        raise ValueError("Envelope UUIDs must contain exactly 16 bytes")
    body = envelope.WhichOneof("body")
    if body is None:
        raise ValueError("Missing envelope body")
    allowed = dict(body_transports(body, profile))
    if transport is not None and transport not in allowed:
        raise ValueError("Message arrived on the wrong transport")
    cap = allowed[transport] if transport is not None else min(allowed.values())
    if envelope.ByteSize() > cap:
        raise ValueError("Envelope exceeds the selected transport cap")
    validate_fields(envelope, profile)
    clean = type(envelope)()
    clean.CopyFrom(envelope)
    clean.DiscardUnknownFields()
    if clean.SerializeToString(deterministic=True) != envelope.SerializeToString(deterministic=True):
        raise ValueError("Unknown wire fields are not part of this exact-hash contract")
    if body == "controller_input":
        sample = envelope.controller_input
        if not all(sample.HasField(name) for name in ("transaction", "capture", "specific_force_m_s2", "angular_velocity_rad_s")):
            raise ValueError("Controller sample is missing required nested input")
        transaction = sample.transaction
        if (transaction.controller_id, transaction.session_id) != (envelope.sender_id, envelope.sender_session_id):
            raise ValueError("Controller sample identity differs from its sender")
        if not all((transaction.request_seq, sample.sample_id, sample.association_version, sample.calibration_id)):
            raise ValueError("Controller sample is missing an identity or binding revision")
        if sample.capture.timing_valid and (not sample.capture.clock_id or not sample.capture.kind):
            raise ValueError("Valid sample capture needs a clock and time kind")
    elif body == "skeleton_frame":
        pose = envelope.skeleton_frame
        if not pose.HasField("capture") or not all((pose.frame_id, pose.person_id, pose.processing_clock_id,
                                                    pose.image_width, pose.image_height, pose.calibration_id, pose.state)):
            raise ValueError("Pose is missing its identity, dimensions or capture metadata")
        if sorted(joint.coco_joint_index for joint in pose.joints) != list(range(17)):
            raise ValueError("Pose needs exactly seventeen distinct COCO joints")
        for joint in pose.joints:
            if not joint.state or not all(0 <= value <= 1 for value in (joint.x_normalized, joint.y_normalized, joint.score)):
                raise ValueError("Joint state or normalized coordinates/score are invalid")
        if pose.capture.timing_valid and (not pose.capture.clock_id or not pose.capture.kind):
            raise ValueError("Valid pose capture needs a clock and time kind")
    elif body == "frame_status":
        ids = list(envelope.frame_status.person_ids)
        if len(set(ids)) != len(ids) or any(not value for value in ids):
            raise ValueError("Frame-status person identities must be distinct and nonzero")
