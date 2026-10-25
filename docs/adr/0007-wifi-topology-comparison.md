# ADR 0007: Retain Wi-Fi and compare external AP with Pi hotspot

- Date: 2026-10-25
- Status: **Agreed planning decision**; topology configuration and measured selection remain open
- Related: [ADR 0005](0005-webcam-wireless-pi3-masterplan.md), [ADR 0006](0006-independent-imu-trigger-markers.md), [network comparison](../networking.md#external-ap-versus-pi-hotspot-comparison)

## Context and decision

The user chose to retain Wi-Fi for now and requested a comparison between an external access point and a Raspberry Pi hotspot. Keep the external AP with wired Pi/laptop as variant A and the initial baseline. Add variant B with controllers associated to the Pi 3 B's onboard hotspot while the laptop remains wired. This refines ADR 0005's deployment assumption without changing component roles.

Both variants retain the continuous 200 Hz controller stream, UDP/Protobuf gameplay, TCP control, full ball-state query/response/commit path, per-transaction identities, deadlines and independent diagnostic markers. No gameplay schema or numerical profile change is introduced. ESP-NOW and other radio transports are deferred outside this work package.

## Evaluation and consequences

Prove address/interface and debug-collector reachability before measurement. Record and hold the Pi hotspot's bridge/routing configuration fixed. Run matched trials at one through four controllers, three 10-minute baselines per count and variant, plus comparable load/fault trials. Preserve failure counts, all-sample and marker timing populations, and observation overhead.

Compare complete response/electrical distributions, failures, batch service, Pi resource use and recovery under the same acceptance criteria. No reduced-latency claim follows from removing a box. Keep A as baseline until evidence supports a recorded deployment selection. No network configuration, hardware run or transport implementation was performed by this planning decision.
