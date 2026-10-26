# Hardware reference and procurement gates

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Network](networking.md)

**User-confirmed:** Raspberry Pi 3 Model B; Windows laptop with RTX 5080; four wireless battery controllers required; **MPU-6050 over I²C with Zephyr for the first prototype**; ESP32 model still open; Elgato Facecam or another webcam considered. **Proposed:** the remaining reference parts and connections below. Exact MPU-6050 breakout and Zephyr/HAL versions remain open. No purchases, electrical design approval, hardware inventory inspection or bench tests were performed.

## Reference bill of materials

| Quantity | Device / part | Decision and verification |
| --- | --- | --- |
| 1, available | Raspberry Pi 3 Model B | Native C++ fusion/physics only; wired 100BASE-T LAN; appropriate micro-USB supply, microSD, cooling and temperature/throttling monitoring |
| 1, available by user report | Windows RTX 5080 laptop | Capture, GPU pose inference, separate state service/renderer and debug collection; verify GPU identity/VRAM, driver, power mode and cooling |
| 4, recommended | ESP32-S3-DevKitC-1-N8R8 | Proposed ESP32 board variant for the selected Zephyr firmware; pin and verify the board/HAL combination, exposed pins and USB debugging; 2.4 GHz Wi-Fi, no assumption of 5 GHz capability |
| 4, selected prototype IMU | MPU-6050 I²C breakout with 3.3 V-compatible I/O and accessible shared INT | Exact module/revision and inventory remain unverified. Validate filter/divider configuration for 200 Hz accel/gyro acquisition, range/saturation, motion-detector delay/semantics and shared-INT source attribution; Zephyr motion handling and early timestamps need extension. See the [prototype assessment and later alternatives](imu-selection.md) |
| 4, recommended | DRV2605L driver board and a matched LRA actuator | Driver/actuator voltage and resonance must be configured from chosen parts; normalized requested intensity is not calibrated physical strength |
| 4, required | External status LED, current limiting, pairing button, rigid grip/enclosure and wrist strap | Distinct hit/miss/fault patterns; camera-visible player label; safe mechanical retention |
| 4, proposed power assembly | Protected 1S rechargeable Li-ion/LiPo pack, nominal 1,200 mAh; charger with power-path management, switch and regulated supply | Reference capacity only; choose compliant assembled parts and a power design matched to board/motor peaks. Cell must never connect directly to a 3.3 V rail. Runtime is measured, not inferred from capacity alone |
| 1, variant A baseline | Dedicated configurable access point with wired LAN/switch | Compare against variant B using Pi 3 B onboard hotspot; four controller stations on quiet legal 2.4 GHz 20 MHz, laptop wired in both; record both actual radio configurations |
| 1, to validate | Webcam capable of 1080p60 at actual whole-body playing distance | Prefer fixed mounting and controllable exposure; exact Facecam generation matters; see tracking stack |
| As needed | Ethernet cables and laptop adapter; rigid camera mount; calibration target | Verify link speed, USB topology and full player visibility |
| 1 set, measurement | Logic analyzer, safe signal leads/common reference, optional photodiode/vibration sensor/light barrier | Compare GPIO and actual electrical outputs; characterize reference uncertainty |

The Pi 3B has a 1.2 GHz quad-core CPU, 1 GB RAM and 100BASE-T Ethernet; it is not a Pi 3B+ or Pi 5. Its USB/Ethernet architecture and thermal state matter under load. See [official specification](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/) and [board documentation](https://www.raspberrypi.com/documentation/computers/sbcs.html). The laptop GPU carries inference; transferring webcam video to the Pi would spend resources without improving the proposed pipeline.

The [ESP32-S3 board guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/) and [SoC specification](https://www.espressif.com/en/products/socs/esp32-s3) establish the recommended board family and 2.4 GHz radio. The [IMU assessment](imu-selection.md) and [ADR 0008](adr/0008-mpu6050-zephyr-prototype.md) select MPU-6050/I²C and Zephyr for the first prototype, superseding BMI270/SPI and ESP-IDF. The [reference profile](../spec/reference-profile.json) retains this selection in `webcam-pi3-doubles-v3`; the 200 Hz stream and timing targets remain unchanged, while [ADR 0011](adr/0011-full-match-contract-and-state-stream.md) separately versions the match-state interface. Later production alternatives remain subject to measured evidence. The [DRV2605L documentation](https://www.ti.com/product/DRV2605L) covers ERM/LRA drive; select and characterize an actual actuator before setting drive limits.

## Proposed controller wiring allocation

This is a proposed pin assignment **only for the named ESP32-S3 DevKitC reference**, not a verified schematic for another ESP32 variant. Check board revision and module pin reservations before wiring. Keep USB GPIO19/20, boot-strapping pins and PSRAM-reserved pins free of these peripherals.

| Signal | Proposed ESP32-S3 GPIO | Electrical/measurement rule |
| --- | --- | --- |
| MPU-6050 I²C SDA / SCL | Open | Select pins after verifying the actual ESP32 board and breakout; validate voltage, pull-ups, bus rate and address configuration. MPU-6050 uses I²C; historical SPI assignments do not apply |
| MPU-6050 shared INT: data-ready and motion | 14, unvalidated proposal | One physical IMU output only. Capture the shared edge and attribute enabled sources through reviewed status/latch/clear handling; preserve unresolved overlap and source/capture time separately |
| Driver I²C SDA / SCL | 8 / 9 | Verify breakout pull-ups and voltage levels; 400 kHz initial bus target |
| External LED | 4 | Current-limiting component chosen from LED characteristics; do not assume onboard RGB LED pin |
| Pairing button | 21 | Debounce outside the IMU interrupt; deliberate re-pairing only |
| Measurement markers | 6 / 7 / 15 | Separate `t0`, complete-result receipt and output-command markers; actual motor drive observed separately |

GPIO is not a motor power supply. The haptic driver and power assembly must handle actuator current and transients. Include local decoupling and a shared signal reference, and check whether vibration/current affects IMU measurements or radio stability. Proposed outputs default off at boot, disconnect, watchdog recovery and invalid driver configuration. A locally enforced 50 ms maximum pulse is independent of network commands.

The MPU-6050 I²C pins and any bus sharing with the haptic driver remain open until wiring and bus-time measurements are reviewed. The driver's existing GPIO8/9 assignment is only a proposed allocation; it does not assign the IMU automatically. Verify that haptic traffic cannot block sensor acquisition or the interrupt-status handling needed for trace provenance.

The [threshold marker](imu-trigger-markers.md) is additional to regular sampling but uses the MPU-6050's shared INT output. Validate simultaneous data-ready and motion status, clearing/latching and missed or overlapping edges under continuous radio traffic. Confirm actual 5 ms sample cadence from the configured filter/divider, and measure sensor detection delay plus IRQ-to-timestamp delay separately. A Zephyr binding alone does not establish motion-handler support, early timestamp capture or absolute-threshold semantics; the selected prototype needs reviewed driver integration. Record false triggers caused by the actuator and any explicit rearm/suppression policy. Acquisition and networking can progress while marker acceptance remains open, but software threshold detection must not silently replace the hardware marker.

## Battery and radio commissioning

Wireless gameplay must run from battery. USB can serve flashing and a stationary timing reference, but is not the gameplay power/transport assumption. Use a reviewed power-path design that prevents back-feeding when USB and battery are connected. The final regulator, charger, connector polarity, fuse/protection, enclosure and actuator part are procurement gates; do not build a generic wiring diagram from an unrelated development board.

Disable Wi-Fi modem sleep during active low-latency play in the selected Zephyr firmware, with Bluetooth disabled. Pin and verify the concrete Zephyr ESP32 driver configuration rather than assuming an ESP-IDF application API applies. This policy increases battery consumption; measure average and peak current across idle, four-player radio load, haptics and low-battery operation. Derive run time from usable energy, conversion loss and measured current, then test the pack's cutoff behavior. Do not promise hours of operation from the nominal mAh value.

## Camera selection and geometry

A close-up webcam's 1080p60 label does not establish usable focus for four whole bodies several metres away. The tracking-stack page distinguishes Facecam/MK.2 and Facecam 4K mode-dependent focus specifications. Before purchase/final selection, verify sharp wrists/ankles across the entire lane layout, exposure under motion, full-frame field of view, sustainable negotiated frame rate and capture timestamps. Avoid wide-angle distortion or software mirroring that is not represented in calibration.

First deployment is a calibrated 2.5D plane/lane model. True metric 3D needs a separately validated stereo/depth/multi-view solution; Kinect v2 is retained only as a possible later alternative. See [tracking stack and sources](tracking-stack.md) and [coordinate calibration](coordinates-and-time.md).

## Hardware acceptance gates

Record exact board/sensor/driver/actuator and webcam revisions, laptop GPU/driver, Pi OS/kernel, supply, AP/channel, cable/USB topology and display mode. Validate safe power/output defaults, IMU saturation/filter delay, camera focus/capture uncertainty, four-player identity, radio tails, Pi throttling and logger overhead. A faster Pi or stronger model is considered only after measurements identify the bottleneck. The remaining component/power choices are explicit build gates, not hidden assumptions.
