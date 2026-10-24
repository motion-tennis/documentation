# Hardware and deployment prerequisites

[Documentation home](../README.md) · [Architecture](architecture.md) · [Development setup](development.md)

**Implemented:** no firmware, wiring diagram, bill of materials, device configuration, or hardware test is present in the inspected repositories. **Agreed design:** ESP32 handheld controllers, an Xbox One Kinect / Kinect v2, a Raspberry Pi for physics, and a PC for the game engine. **Proposed:** the connection and commissioning guidance below. **Open:** exact parts and operating environments not established by repository evidence.

## Device allocation

| Physical device | Software role | Known requirements | Open choices |
| --- | --- | --- | --- |
| One to four handheld controllers | Controller firmware | ESP32, Wi-Fi, IMU with an interrupt or documented measurement boundary, LED, vibration motor | ESP32 variant, board, IMU, power source, framework, driver, pins, enclosure |
| Xbox One Kinect / Kinect v2 | Input to camera-tracking service | Sensor, suitable power/PC adapter and USB connection | Available adapter, USB-host compatibility, mounting, tracking backend |
| Raspberry Pi | Physics component | Network path to controllers, tracking service, and game engine | Pi model, OS, architecture, cooling, wired versus wireless uplink |
| PC | Game engine and optionally camera-tracking service | Display and network; Linux is the intended game-engine environment | Rendering framework, Linux distribution, GPU needs, tracking service OS |
| Local network infrastructure | Connects distributed components | Wi-Fi coverage for all controllers | Access point, channel, addressing, congestion controls, security configuration |

The handheld controllers are ESP32 devices. The Raspberry Pi is the physics host. Sharing one physical PC for tracking and rendering does not merge their software responsibilities or repositories.

For a Kinect v2 host, the upstream libfreenect2 driver requires USB 3.0; USB 2 is unsupported. Validate the available host controller and adapter with the actual sensor rather than assuming connector shape proves compatibility. See the [upstream hardware requirements](https://github.com/OpenKinect/libfreenect2#hardware-requirements). This is a dependency requirement, not a Motion Tennis hardware test result.

## Controller wiring information

No pinout is agreed. Do not copy an unrelated ESP32 board's pin numbers into firmware. Before wiring, record a reviewed table containing the selected board revision, signal names, connector orientation, voltage levels, supply/current requirements, driver part, and selected GPIO capabilities.

| Functional connection | Required information before implementation |
| --- | --- |
| IMU data bus to ESP32 | Selected IMU and bus, voltage compatibility, addressing or chip select, required passives, sample rate and filtering |
| IMU interrupt to ESP32 | Interrupt meaning, polarity, edge/level mode, usable input pin, and whether buffered samples predate the interrupt |
| ESP32 output to LED | LED type, driver/current limiting, polarity, output pin, measurable electrical activation point |
| ESP32 output to vibration driver | Motor type, rated supply/current, driver and protection requirements, control mode, enable pin, default-off behavior |
| Power and reference | Supply capacity under Wi-Fi and motor load, grounding, decoupling, startup/reset behavior |
| Measurement test points | IMU interrupt, transaction marker, LED command, motor command, and analyzer reference |

The motor requires a suitable power/driver circuit; an ESP32 GPIO must not be treated as a motor power supply. The electrical design must be derived from the selected component datasheets. No generic motor circuit or invented pin assignment is a project schematic.

**Proposed:** default feedback outputs to off during reset, watchdog recovery, disconnect, and firmware startup; cap duty/intensity and pulse duration in a locally enforced profile. Measure whether motor current disturbs the IMU, Wi-Fi, or supply before interpreting latency traces. See [controller behavior](controller.md).

## Kinect and host decision

The first feasibility milestone must establish continuous multi-person joint tracking on the actual Kinect v2, with stable identities, capture timestamps, quality flags, and a measured processing delay. A working depth image alone does not satisfy gameplay requirements.

Microsoft's SDK 2.0 download page lists Windows 8, Windows 8.1, and Windows Embedded Standard 8, along with x64, USB 3.0, and a DirectX 11-capable graphics adapter. Those published requirements describe an alternative dependency route; they do not establish this project's installed OS, newer Windows support, or Linux body tracking. See the [official SDK requirements](https://www.microsoft.com/en-us/download/details.aspx?id=44561).

If a Windows-only tracking solution is selected, record the deployment change explicitly: tracking may need a separate Windows host while the game engine remains on its intended Linux PC. Do not silently assume both services can still share one OS. The [tracking decision](tracking.md#backend-selection) is open.

## Proposed commissioning record

For each experiment, retain a hardware inventory with controller ID and board revision, sensor model and settings, firmware revision, Pi model/OS, PC CPU/GPU/OS, Kinect adapter/USB host, network topology, and display refresh configuration. Store serial numbers only where needed for reproducibility; do not put network credentials in the repository.

Commission in stages: power and default-off feedback, local IMU acquisition, timestamp/GPIO comparison, network exchange with synthetic data, Kinect tracking and calibration, then integrated play. Record environmental conditions such as camera placement, player distance and occlusion, Wi-Fi interference, CPU load, and power throttling. These are proposed activities; no successful commissioning is claimed.

## Required decisions

The team must choose a board/IMU/driver/power combination, tracking backend and OS, Pi model and OS, network configuration, and available timing instruments. Record each selection with a reproducible configuration and validation evidence in the relevant repository and [decision log](adr/README.md). Hardware availability can be resolved independently of protocol and documentation work.
