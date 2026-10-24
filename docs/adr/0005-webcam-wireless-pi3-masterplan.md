# ADR 0005: Webcam-first wireless four-player reference

[Decision index](README.md) · [Master plan](../master-plan.md)

**Status:** User-confirmed constraints and proposed reference implementation, 2026-10-24. Supersedes hardware/deployment assumptions in ADR 0001 and transport/backend proposal ADR 0004; refines ADR 0002. Runtime implementation and measurements are absent.

## Confirmed inputs

Available Raspberry Pi 3 Model B and Windows RTX 5080 laptop; four wireless battery controllers required; ESP32 and webcam models not yet fixed. First use calibrated webcam 2.5D gameplay, then true 3D. Add `debug-units` as the sixth repository. Keep every repository edit, code and comment in English.

## Reference choices

- Recommend ESP32-S3/ESP-IDF with BMI270 SPI at 200 Hz and a characterized LED/LRA driver/power assembly. Do not claim selected purchase or tested pinout.
- Run webcam capture/rectification and RTMO-m 640 GPU inference on Windows. Use separate person identity tracking and intentional controller association. Prohibit invented monocular metric depth.
- Run native C++ fusion/physics on Pi 3 with wired 100BASE-T to a dedicated AP/LAN; controllers use 2.4 GHz Wi-Fi. Keep webcam video/GPU work off Pi.
- Use UDP/Protobuf ≤ 1,200 bytes for live messages and framed TCP for control. Keep source/transaction IDs, bounded queues, explicit expiry, deduplication and schema/profile hashes.
- Group up to 8 inputs/max 2 per controller into one required query/response exchange carrying all logical query keys. From the common snapshot, evaluate ordered events and atomically commit final state and staged gameplay side-state before individual feedback. Retain one state batch in flight and periodic-only motion.
- Keep committed state in a separate native Windows service and use a simple separate SDL3 renderer. GPU/render delays must not intentionally block state replies.
- Define 30/40 ms p99 application/electrical targets and 50 ms controller expiry. These are measured acceptance targets, not hard real-time guarantees. Preserve controller-local RTT and separate physical-onset experiments.
- Specify a complete asynchronous debug environment; implement only the small offline trace audit/fixtures/tests in this documentation phase.

## Consequences and alternatives

The mandatory ball-state query remains but batching reduces per-sample PC exchanges. The 8-entry cap gives headroom beyond four nominal arrivals per tick; feasibility still depends on measured Pi/Windows/radio tails. Stale inputs fail visibly rather than silently changing sampling semantics. Commit-uncertain or paused time is handled explicitly without hidden state divergence.

Dedicated Wi-Fi is practical for the required untethered controllers but cannot establish a worst-case bound. ESP-NOW is a comparison option with extra gateway/application work; USB is a stationary measurement reference, not the gameplay plan. A faster Pi is an evidence-driven fallback, not an assumed prerequisite. Camera/model selection depends on whole-body focus, identity, time uncertainty and model/runtime compatibility, not GPU marketing alone.

The approved 2.5D simplification is an explicit geometric constraint. True 3D requires a new calibrated depth/stereo/multi-view contract. Calibration residuals and confidence thresholds are validation gates; a smooth avatar cannot prove collision accuracy.

## Required validation

Compile shared codecs and test maximum encoded sizes; prove four-person GPU tracking on the actual camera/laptop; benchmark Pi 3 wired-state batch capacity; characterize one battery controller; then run one-to-four-controller timing/fault trials with complete trace accounting. Current offline tests are synthetic and satisfy none of those hardware gates. See [testing](../testing.md) and [roadmap](../roadmap.md).
