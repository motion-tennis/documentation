# Hardware reference and procurement gates

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Network](networking.md)

**User-confirmed:** Raspberry Pi 3 Model B; Windows laptop with RTX 5080; four wireless battery controllers required; ESP32 model still open; Elgato Facecam or another webcam considered. **Proposed:** the reference parts and connections below. No purchases, electrical design approval, hardware inventory inspection or bench tests were performed.

## Reference bill of materials

| Quantity | Device / part | Decision and verification |
| --- | --- | --- |
| 1, available | Raspberry Pi 3 Model B | Native C++ fusion/physics only; wired 100BASE-T LAN; appropriate micro-USB supply, microSD, cooling and temperature/throttling monitoring |
| 1, available by user report | Windows RTX 5080 laptop | Capture, GPU pose inference, separate state service/renderer and debug collection; verify GPU identity/VRAM, driver, power mode and cooling |
| 4, recommended | ESP32-S3-DevKitC-1-N8R8 | ESP-IDF C/C++; explicit exposed pins and USB debugging; 2.4 GHz Wi-Fi, no assumption of 5 GHz capability |
| 4, recommended | BMI270 breakout exposing SPI, data-ready interrupt and 3.3 V-compatible I/O | Start accelerometer and gyro at 200 Hz, ±16 g and ±2000 degrees/s; convert wire angular rates to rad/s and flag saturation; verify exact filter/group delay |
| 4, recommended | DRV2605L driver board and a matched LRA actuator | Driver/actuator voltage and resonance must be configured from chosen parts; normalized requested intensity is not calibrated physical strength |
| 4, required | External status LED, current limiting, pairing button, rigid grip/enclosure and wrist strap | Distinct hit/miss/fault patterns; camera-visible player label; safe mechanical retention |
| 4, proposed power assembly | Protected 1S rechargeable Li-ion/LiPo pack, nominal 1,200 mAh; charger with power-path management, switch and regulated supply | Reference capacity only; choose compliant assembled parts and a power design matched to board/motor peaks. Cell must never connect directly to a 3.3 V rail. Runtime is measured, not inferred from capacity alone |
| 1, recommended | Dedicated configurable access point with wired LAN/switch | Four controller stations on a quiet legal 2.4 GHz 20 MHz channel, Pi/laptop wired; no Pi-hosted AP |
| 1, to validate | Webcam capable of 1080p60 at actual whole-body playing distance | Prefer fixed mounting and controllable exposure; exact Facecam generation matters; see tracking stack |
| As needed | Ethernet cables and laptop adapter; rigid camera mount; calibration target | Verify link speed, USB topology and full player visibility |
| 1 set, measurement | Logic analyzer, safe signal leads/common reference, optional photodiode/vibration sensor/light barrier | Compare GPIO and actual electrical outputs; characterize reference uncertainty |

The Pi 3B has a 1.2 GHz quad-core CPU, 1 GB RAM and 100BASE-T Ethernet; it is not a Pi 3B+ or Pi 5. Its USB/Ethernet architecture and thermal state matter under load. See [official specification](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/) and [board documentation](https://www.raspberrypi.com/documentation/computers/sbcs.html). The laptop GPU carries inference; transferring webcam video to the Pi would spend resources without improving the proposed pipeline.

The [ESP32-S3 board guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/) and [SoC specification](https://www.espressif.com/en/products/socs/esp32-s3) establish the recommended board family and 2.4 GHz radio. The [BMI270 datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi270-ds000.pdf) and [official SensorAPI](https://github.com/boschsensortec/BMI270_SensorAPI) are the implementation references. The [DRV2605L documentation](https://www.ti.com/product/DRV2605L) covers ERM/LRA drive; select and characterize an actual actuator before setting drive limits.

## Proposed controller wiring allocation

This is a proposed pin assignment **only for the named ESP32-S3 DevKitC reference**, not a verified schematic for another ESP32 variant. Check board revision and module pin reservations before wiring. Keep USB GPIO19/20, boot-strapping pins and PSRAM-reserved pins free of these peripherals.

| Signal | Proposed ESP32-S3 GPIO | Electrical/measurement rule |
| --- | --- | --- |
| BMI270 SPI chip select | 10 | 3.3 V-compatible breakout; SPI mode and initialization from sensor datasheet |
| SPI clock / MOSI / MISO | 12 / 11 / 13 | Start at a conservative 4 MHz; confirm signal quality and supported sensor bus mode |
| IMU data-ready interrupt | 14 | Timestamp the documented interrupt edge; preserve FIFO/source time separately |
| Driver I²C SDA / SCL | 8 / 9 | Verify breakout pull-ups and voltage levels; 400 kHz initial bus target |
| External LED | 4 | Current-limiting component chosen from LED characteristics; do not assume onboard RGB LED pin |
| Pairing button | 21 | Debounce outside the IMU interrupt; deliberate re-pairing only |
| Measurement markers | 6 / 7 / 15 | Separate `t0`, complete-result receipt and output-command markers; actual motor drive observed separately |

GPIO is not a motor power supply. The haptic driver and power assembly must handle actuator current and transients. Include local decoupling and a shared signal reference, and check whether vibration/current affects IMU measurements or radio stability. Proposed outputs default off at boot, disconnect, watchdog recovery and invalid driver configuration. A locally enforced 50 ms maximum pulse is independent of network commands.

## Battery and radio commissioning

Wireless gameplay must run from battery. USB can serve flashing and a stationary timing reference, but is not the gameplay power/transport assumption. Use a reviewed power-path design that prevents back-feeding when USB and battery are connected. The final regulator, charger, connector polarity, fuse/protection, enclosure and actuator part are procurement gates; do not build a generic wiring diagram from an unrelated development board.

Disable Wi-Fi modem sleep during active low-latency play in the reference firmware, with Bluetooth disabled. This increases battery consumption; measure average and peak current across idle, four-player radio load, haptics and low-battery operation. Derive run time from usable energy, conversion loss and measured current, then test the pack's cutoff behavior. Do not promise hours of operation from the nominal mAh value.

## Camera selection and geometry

A close-up webcam's 1080p60 label does not establish usable focus for four whole bodies several metres away. The tracking-stack page distinguishes Facecam/MK.2 and Facecam 4K mode-dependent focus specifications. Before purchase/final selection, verify sharp wrists/ankles across the entire lane layout, exposure under motion, full-frame field of view, sustainable negotiated frame rate and capture timestamps. Avoid wide-angle distortion or software mirroring that is not represented in calibration.

First deployment is a calibrated 2.5D plane/lane model. True metric 3D needs a separately validated stereo/depth/multi-view solution; Kinect v2 is retained only as a possible later alternative. See [tracking stack and sources](tracking-stack.md) and [coordinate calibration](coordinates-and-time.md).

## Hardware acceptance gates

Record exact board/sensor/driver/actuator and webcam revisions, laptop GPU/driver, Pi OS/kernel, supply, AP/channel, cable/USB topology and display mode. Validate safe power/output defaults, IMU saturation/filter delay, camera focus/capture uncertainty, four-player identity, radio tails, Pi throttling and logger overhead. A faster Pi or stronger model is considered only after measurements identify the bottleneck. The remaining component/power choices are explicit build gates, not hidden assumptions.
