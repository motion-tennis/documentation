# Zephyr evaluation setup: ESP32-S3-Zero

[Documentation home](../README.md) · [Hardware](hardware.md) · [Development setup](development.md) · [Troubleshooting](troubleshooting.md)

**Status:** evaluation record, 2026-11-22. A minimal Zephyr application was compiled, flashed and observed running on one Waveshare ESP32-S3-Zero module. Building, flashing and monitoring from VS Code through the WSL extension was also confirmed by the user. The Wi-Fi and Protobuf extension in [Part 5](#part-5-wi-fi-and-protobuf-encoding) has been compiled and its encoding checked on a host; Wi-Fi connection and UDP delivery on the device are not yet recorded. This is a toolchain and board-definition evaluation only. It does not change the recommended controller board in [Hardware](hardware.md) (ESP32-S3-DevKitC-1-N8R8), does not validate the controller firmware, and does not establish electrical, timing or Wi-Fi behaviour.

The work has two separate layers:

1. **Board definition (once per board type).** Zephyr has no upstream board for the ESP32-S3-Zero. A custom board definition was created first. It describes the hardware (SoC, flash/PSRAM, console, onboard LED, button) and is the foundation that every application for this board builds on.
2. **Application project (once per application).** A normal Zephyr application (`CMakeLists.txt`, `prj.conf`, `src/main.c`, overlay) that selects the custom board as its build target. Any number of applications can use the same board definition.

The host toolchain (WSL2, Zephyr workspace, SDK) is set up once per development machine and is needed for both layers.

## Verified versions

| Component | Version used |
| --- | --- |
| Host | Windows with WSL 2, Ubuntu 26.04.1 LTS |
| Zephyr | v4.4.0 |
| `hal_espressif` | `b7953b8019361d09e613f7011d2ccc41b984d087` (pinned by Zephyr v4.4.0) |
| Zephyr SDK | 1.0.1, toolchain `xtensa-espressif_esp32s3_zephyr-elf` (GCC 14.3.0) |
| `nanopb` module | `5499fd4c9a478f8139eeb07a82c3b4468d6067f7`, nanopb 1.0.0-dev (pinned by Zephyr v4.4.0) |
| `mbedtls` module | `a3e190fe44c78d1ba67f55979e1257328cc7d0d8` (pinned by Zephyr v4.4.0) |
| `tf-psa-crypto` module | `dc575a2ddcc8cb16275d24c42a52eaf79ebe2231` (pinned by Zephyr v4.4.0) |
| west / esptool | 1.5.0 / 5.6.0 |
| CMake / Python / dtc | 4.2.3 / 3.14.4 / 1.7.2 |
| zephyr-utilities | 0.2.0, commit `08f2bb0` |
| Board target | `esp32s3_zero/esp32s3/procpu` |

## Part 1: Board definition (foundation)

### Why a custom board is needed

Upstream Zephyr v4.4.0 contains no `esp32s3_zero` board. The closest upstream board is `waveshare/esp32s3_matrix`, which uses the same module class (ESP32-S3FH4R2: 4 MB flash, 2 MB PSRAM, native USB Serial/JTAG console). It differs in the onboard LED: an 8×8 WS2812 matrix on GPIO14 instead of a single WS2812 on GPIO21.

### How it was created

The board was generated with the zephyr-utilities **Project Creator → Custom boards → Create** workflow:

- Reference board: `esp32s3_matrix` (vendor `waveshare`)
- New board identifier: `esp32s3_zero`, vendor `waveshare`, display name `ESP32-S3-Zero`
- Result: an independent board root containing `boards/waveshare/esp32s3_zero/`, with renamed files, license evidence and `zephyr-board-origin.json` recording the reference source

The generated copy is a starting point for the reference hardware. These manual changes adapt it to the ESP32-S3-Zero:

| File | Change |
| --- | --- |
| `esp32s3_zero-pinctrl.dtsi` | WS2812 data pin `SPIM2_MOSI_GPIO14` → `SPIM2_MOSI_GPIO21` |
| `esp32s3_zero_esp32s3_procpu.dts` | `chain-length` 64 → 1; removed the `rgb_matrix` node and `zephyr,display` |
| `esp32s3_zero_esp32s3_procpu.yaml` | removed `display` from `supported` |
| both `*.dts` | `compatible` and `model` renamed from Matrix to Zero |

The `led-strip` alias, BOOT button (`sw0`, GPIO0), flash and PSRAM sizes and partition table are inherited unchanged. GPIO21 and RGB colour order were confirmed by observation on one module (red, green and blue displayed as expected).

**Known zephyr-utilities limitation:** with Zephyr v4.5.0 or current `main`, custom board creation fails with *"This checkout's REUSE license annotations need a newer sample adapter"*. The parser in `features/projects/samples.py` (`_licenses`) only accepts the older single-annotation `REUSE.toml`. Use Zephyr v4.4.0 or create the board files manually.

### Location and use

The board root is currently stored outside this repository as `Projekt/esp32s3_zero-board/` and in the workspace as `~/zephyrproject/hardware/esp32s3_zero/`. Builds reference it with `-DBOARD_ROOT=<path>`, or it is registered once in zephyr-utilities (**Custom boards → Register**, followed by **Analyze**). The Device Tree Editor in zephyr-utilities 0.2.0 does not support ESP32 chips; pin assignments are edited manually in application overlays.

## Part 2: Host toolchain (once per machine)

All Linux commands run in the Ubuntu WSL shell, inside the Linux home directory. Do not place the workspace on `/mnt/c` or `/mnt/d` (slow file access; cloud-sync folders would synchronise build output).

### 2.1 WSL 2 and Ubuntu

In PowerShell as administrator:

```powershell
wsl --update
wsl --install -d Ubuntu
wsl --set-default Ubuntu
wsl -l -v
```

`Ubuntu` must show `VERSION 2` and be marked as default (`*`). The versioned name `Ubuntu-24.04` was not offered by `wsl --list --online` on this machine. Open the shell with `wsl ~` (not `wsl -d Ubuntu ~`, which treats `~` as a command).

### 2.2 System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y --no-install-recommends \
  git cmake ninja-build gperf ccache dfu-util device-tree-compiler \
  wget curl python3-dev python3-venv python3-pip python3-tk \
  xz-utils file make gcc g++ libmagic1 usbutils
```

Zephyr v4.4.0 requires Python 3.12 or newer.

### 2.3 Zephyr workspace v4.4.0

```bash
mkdir -p ~/zephyrproject
python3 -m venv ~/zephyrproject/.venv
source ~/zephyrproject/.venv/bin/activate
pip install west
west init -m https://github.com/zephyrproject-rtos/zephyr --mr v4.4.0 ~/zephyrproject
cd ~/zephyrproject
west config manifest.project-filter -- '-.*,+hal_espressif'
west update
west zephyr-export
west packages pip --install
west blobs fetch hal_espressif
```

The project filter downloads only `hal_espressif` instead of all modules. Remove it with `west config -d manifest.project-filter` and run `west update` if other modules are needed. `west packages pip --install` also installs `esptool`; without it the ESP32 build stops in CMake with *"esptool>=5.0.2 not found in PATH"*. `west list` must show `zephyr` and `hal_espressif`. Wi-Fi and Protobuf encoding need three more modules; see [Part 5.1](#51-additional-west-modules).

Activate the environment in every new shell: `source ~/zephyrproject/.venv/bin/activate`.

### 2.4 Zephyr SDK

```bash
west sdk install -t xtensa-espressif_esp32s3_zephyr-elf
~/zephyr-sdk-1.0.1/gnu/xtensa-espressif_esp32s3_zephyr-elf/bin/xtensa-espressif_esp32s3_zephyr-elf-gcc --version
```

This installs only the minimal SDK and the ESP32-S3 toolchain into `~/zephyr-sdk-1.0.1`.

### 2.5 zephyr-utilities and board root (optional UI)

```bash
git clone https://github.com/VikoHofer/zephyr-utilities ~/zephyrproject/zephyr-utilities
pip install -e ~/zephyrproject/zephyr-utilities
mkdir -p ~/zephyrproject/hardware
cp -r <source>/esp32s3_zero-board ~/zephyrproject/hardware/esp32s3_zero
```

Start the UI with `zephyr-utils` from `~/zephyrproject` and open `http://127.0.0.1:8765` in the Windows browser. Clone rather than copy zephyr-utilities from a Windows checkout, because Windows line endings can break Linux scripts.

### 2.6 USB access from WSL

WSL does not see USB devices without [usbipd-win](https://github.com/dorssel/usbipd-win). In PowerShell as administrator:

```powershell
winget install --exact dorssel.usbipd-win
usbipd list
usbipd bind --force --busid <BUSID>
usbipd attach --wsl --busid <BUSID> --auto-attach
```

- The ESP32-S3-Zero appears as `303a:1001`, *USB JTAG/serial debug unit*. Its BUSID depends on the USB port.
- `--force` is required only when USBPcap (for example from Wireshark) is installed. Check that `usbipd list` shows `Shared (forced)`, then unplug and replug the board. A Windows restart was additionally needed on this machine.
- While attached to WSL the board is not available to Windows (no COM port). Release it with `usbipd unbind --busid <BUSID>`.
- Keep the `--auto-attach` window open: the chip re-enumerates during flashing and would otherwise stay detached.

> **Manual step:** `usbipd attach` is never run automatically, neither by west, VS Code tasks nor zephyr-utilities. After every Windows restart, WSL restart (`wsl --terminate`, `wsl --shutdown`) or change of USB port, start it yourself in an administrator PowerShell and keep that window open. `bind --force` is persistent per port and only repeated for a new BUSID. Check with `usbipd list` (state `Attached`) and `ls /dev/ttyACM*` in Ubuntu before flashing.

In Ubuntu, once:

```bash
sudo usermod -aG dialout $USER
```

Then close the shell, run `wsl --terminate Ubuntu` in PowerShell and reopen Ubuntu. The board is available as `/dev/ttyACM0`.

## Part 3: Application project (per application)

### 3.1 Create the project

The evaluation application `zero_blink` was created with zephyr-utilities (**Create application**, template `minimal-c`, target `esp32s3_zero/esp32s3/procpu`) and then changed to cycle the onboard RGB LED through red, green and blue every 500 ms using the `led_strip` API (`CONFIG_LED_STRIP=y`). It is stored as `Projekt/zero_blink/` and in the workspace as `~/zephyrproject/apps/zero_blink/`.

Generated projects contain an empty board-specific overlay `overlays/esp32s3_zero_esp32s3_procpu.overlay`, included automatically by `CMakeLists.txt`. Application hardware such as the MPU-6050 I²C bus belongs there, not in the board definition. Projects do not depend on zephyr-utilities at build time.

### 3.2 Build

```bash
cd ~/zephyrproject
source .venv/bin/activate
west build -p -b esp32s3_zero/esp32s3/procpu apps/zero_blink -d build/zero_blink \
  -- -DBOARD_ROOT=$HOME/zephyrproject/hardware/esp32s3_zero
```

The verified build ends with `Successfully created ESP32-S3 image.` and uses 135,240 B of 4 MB flash.

### 3.3 Flash and monitor

With the board attached (Part 2.6):

```bash
west flash -d build/zero_blink
python -m serial.tools.miniterm --exit-char 24 /dev/ttyACM0 115200
```

`--exit-char 24` makes **Ctrl+X** quit the monitor; the default **Ctrl+]** is not reachable on a German keyboard layout. If no port is detected, add `--esp-device /dev/ttyACM0` to `west flash`. If flashing fails, enter download mode: hold **BOOT**, press **RESET**, release **BOOT**.

Expected result: the onboard LED cycles red → green → blue and the monitor prints `LED: red`, `LED: green`, `LED: blue`.

## Part 4: VS Code (optional)

VS Code runs on Windows and works inside Ubuntu through the WSL extension. Editing, building, flashing and the serial monitor all run in WSL.

### 4.1 Install and open

1. Install VS Code for Windows (not inside Ubuntu) and the **WSL** extension (`ms-vscode-remote.remote-wsl`).
2. Copy the prepared configuration into the west workspace and open it from the Ubuntu shell:

   ```bash
   cd ~/zephyrproject
   mkdir -p .vscode
   cp <source>/zephyr-vscode/*.json .vscode/
   code .
   ```

   The first `code .` installs the VS Code Server in Ubuntu. The status bar must show **WSL: Ubuntu**.
3. Install the recommended extensions when prompted. Check in the Extensions view that each one is listed under **WSL: Ubuntu – Installed**; an extension installed only on the Windows side does not work in the WSL window.

The configuration is currently stored outside this repository as `Projekt/zephyr-vscode/`:

| File | Content |
| --- | --- |
| `extensions.json` | Recommends C/C++ (`ms-vscode.cpptools`), Python, DeviceTree (`plorefice.devicetree`) and Kconfig (`trond-snekvik.kconfig-lang`). Marks CMake Tools as unwanted, because it configures CMake itself and conflicts with west |
| `settings.json` | IntelliSense from `build/zero_blink/compile_commands.json`; Python interpreter and integrated terminals use `~/zephyrproject/.venv`; file associations for `.overlay`, `.dtsi`, `.conf`; watcher exclusions for `build`, `.venv`, `zephyr`, `modules` |
| `c_cpp_properties.json` | Explicit IntelliSense configuration `Zephyr ESP32-S3`: compile database and the ESP32-S3 cross compiler from the SDK |
| `tasks.json` | Build, pristine build, flash, monitor and a combined build + flash + monitor task, all with the venv on `PATH`; build errors use the `$gcc` problem matcher |

### 4.2 Use

| Action | How |
| --- | --- |
| Build | **Ctrl+Shift+B**, enter the folder name below `apps/` (default `zero_blink`) |
| Flash / monitor / all | **Ctrl+Shift+P** → *Tasks: Run Task* → `Zephyr: Flash`, `Zephyr: Monitor`, `Zephyr: Build + Flash + Monitor` |
| Quit monitor | **Ctrl+X**, or close the terminal |

All tasks use the target `esp32s3_zero/esp32s3/procpu` and `-DBOARD_ROOT=${workspaceFolder}/hardware/esp32s3_zero`. IntelliSense, including Ctrl+click on `#include <zephyr/...>`, becomes available after the first build, because the compile database is generated by the build. Select the configuration once with **C/C++: Select a Configuration…** → `Zephyr ESP32-S3`. For another application, change the `compileCommands` path in `c_cpp_properties.json` and `settings.json`.

> **Manual step:** the flash and monitor tasks need the board attached to WSL. VS Code does not run `usbipd attach`; start it yourself as described in [Part 2.6](#26-usb-access-from-wsl) and keep the window open.

On-chip debugging through the built-in USB JTAG with OpenOCD was not set up in this evaluation.

## Part 5: Wi-Fi and Protobuf encoding

The `zero_blink` test application was extended to encode every IMU sample as `motion.v03.Envelope { controller_input }` from [`spec/motion.proto`](../spec/motion.proto) with nanopb and to send it over Wi-Fi/UDP as described in the [protocol](protocol.md). This part lists everything needed beyond Parts 2–4. All commands run in the Ubuntu WSL shell with the workspace venv active, unless marked as Windows.

### 5.1 Additional west modules

| Module | Workspace path | Needed for |
| --- | --- | --- |
| `hal_espressif` | `modules/hal/espressif` | ESP32-S3 HAL and the Wi-Fi driver (already in Part 2.3) |
| `nanopb` | `modules/lib/nanopb` | Protobuf runtime and code generator (`CONFIG_NANOPB`) |
| `mbedtls` | `modules/crypto/mbedtls` | Selected by the ESP32 Wi-Fi driver (`WIFI_ESP32` selects `MBEDTLS`) for WPA2 |
| `tf-psa-crypto` | `modules/crypto/tf-psa-crypto` | Crypto core that `mbedtls` builds on in Zephyr v4.4.0 |

Extend the project filter from Part 2.3 and download the modules:

```bash
cd ~/zephyrproject
west config manifest.project-filter -- '-.*,+hal_espressif,+nanopb,+mbedtls,+tf-psa-crypto'
west update
west list
```

`west list` must now show five entries. The manifest also contains `mbedtls-3.6`; it is not needed. Without `mbedtls` the build stops in Kconfig, without `tf-psa-crypto` in CMake (see [Observed problems](#observed-problems)).

### 5.2 Espressif binary blobs

The Wi-Fi driver links Espressif's precompiled Wi-Fi/PHY libraries. They are fetched once with `west blobs fetch hal_espressif` (already part of Part 2.3) and must be fetched again after `hal_espressif` changes revision. `WIFI_ESP32` depends on these blobs. `-DCONFIG_BUILD_ONLY_NO_BLOBS=y` compiles without them but produces firmware that cannot use Wi-Fi; it is only a CI/compile check.

### 5.3 Protobuf host tools

The nanopb generator runs during the build and needs `protoc` and the Python `protobuf` package in the workspace venv:

```bash
sudo apt install -y protobuf-compiler
source ~/zephyrproject/.venv/bin/activate
pip install protobuf grpcio-tools
protoc --version
```

`grpcio-tools` provides a bundled `protoc` as an alternative to the system package; installing both is harmless.

The application keeps copies of [`spec/motion.proto`](../spec/motion.proto) and [`scripts/contract/motion.options`](../scripts/contract/motion.options) in `proto/` and generates `motion.pb.c/.h` with `zephyr_nanopb_sources()` in `CMakeLists.txt`. The copies must stay identical to this repository. Zephyr v4.4.0 ships nanopb 1.0.0-dev, whereas the [contract checks](s0-baseline.md#reproduce-the-contract-evidence) pin nanopb 0.4.9.1. One encoded `controller_input` (133 bytes) was decoded with Python protobuf and was byte-identical to the canonical re-encoding; this is a single host check, not contract evidence for the device codec.

### 5.4 Devicetree and Kconfig

The SoC devicetree disables Wi-Fi and the custom board inherits that from `esp32s3_matrix`, so the application overlay enables it:

```dts
&wifi {
	status = "okay";
};
```

Kconfig options used by `zero_blink` (`prj.conf`):

| Options | Purpose |
| --- | --- |
| `CONFIG_WIFI`, `CONFIG_NETWORKING`, `CONFIG_NET_IPV4`, `CONFIG_NET_UDP`, `CONFIG_NET_DHCPV4`, `CONFIG_NET_SOCKETS` | Wi-Fi station, IPv4 via DHCP, UDP sockets. `CONFIG_NET_IPV6` and `CONFIG_NET_TCP` are disabled |
| `CONFIG_NET_MGMT`, `CONFIG_NET_MGMT_EVENT`, `CONFIG_NET_MGMT_EVENT_INFO`, `CONFIG_NET_MGMT_EVENT_QUEUE_SIZE=16` | Connect request and connection/IPv4 events |
| `CONFIG_NANOPB` | Protobuf encoding |
| `CONFIG_ENTROPY_GENERATOR` | Random 16-byte sender session ID at every boot |
| `CONFIG_EVENTS` | `k_event` used for the network-ready state |
| `CONFIG_MAIN_STACK_SIZE=4096`, `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=4096` | Stack for Wi-Fi start and the connect work item |

The driver's default `CONFIG_ESP32_WIFI_STA_AUTO_DHCPV4` starts DHCP after association. The application disables Wi-Fi power save after connecting (`NET_REQUEST_WIFI_PS`, `WIFI_PS_DISABLED`), as required in [Hardware](hardware.md#battery-and-radio-commissioning). The ESP32-S3 supports 2.4 GHz only.

### 5.5 Credentials and receiver address

| File | Content |
| --- | --- |
| `src/wifi_credentials.h` | `WIFI_SSID`, `WIFI_PASSWORD` (WPA2-PSK). Created from `wifi_credentials.h.example`; listed in `.gitignore` and never committed |
| `src/app_config.h` | `APP_RECEIVER_IPV4`, `APP_RECEIVER_PORT` (41000), `APP_CONTROLLER_ID`, `APP_CLOCK_ID` |
| `src/imu.c` | `IMU_SAMPLE_RATE_HZ` (10 for console tests; the [reference profile](../spec/reference-profile.json) requires 200), `IMU_USE_SIMULATED_DATA` (generated data without the MPU-6050) |

After changing the overlay, `prj.conf` or `CMakeLists.txt`, run a pristine build.

### 5.6 Test receiver on Windows

`tools/udp_receiver.py` in `zero_blink` decodes the messages, checks canonical encoding, marks missing, late and duplicate samples and shows receive rate, interval mean ± standard deviation, relative delay jitter and loss in a status line. Run it on Windows, not in WSL: with the default NAT networking, WSL 2 is not reachable from the ESP32 without port forwarding.

Python 3.12 in a virtual environment outside cloud-synchronised folders (PowerShell):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
py -3.12 -m venv $env:USERPROFILE\venvs\motion-proto
& $env:USERPROFILE\venvs\motion-proto\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install protobuf grpcio-tools
python <path>\zero_blink\tools\udp_receiver.py
```

With Anaconda, use `conda create -n motion-proto python=3.12`, `conda activate motion-proto` and the same `pip install`; run `conda init powershell` once to use `conda activate` in PowerShell. Install the two packages with pip rather than conda so that `protobuf` matches the version `grpcio-tools` requires.

Set `APP_RECEIVER_IPV4` to the laptop's Wi-Fi IPv4 address (`ipconfig`) and allow Python through Windows Defender Firewall for private networks when prompted. The status line needs an ANSI-capable terminal such as Windows Terminal or the VS Code terminal; otherwise use `--no-status-line`.

### 5.7 Limitations of the test firmware

The firmware samples with a timer instead of the MPU-6050 data-ready interrupt, so `t0` is the timer wake-up. `run_id`, association, calibration and battery fields are placeholders and no `hello` or clock exchange exists; a receiver that validates these fields per the [protocol](protocol.md) will reject the messages. These are test simplifications, not contract changes.

## Observed problems

| Symptom | Cause / resolution |
| --- | --- |
| `wsl --install -d Ubuntu-24.04` fails with `WSL_E_DISTRO_NOT_FOUND` | Use a name from `wsl --list --online`, here `Ubuntu` |
| `usbipd attach` reports `Failed to attach device` | USBPcap filter present: `usbipd bind --force`, replug, restart Windows if needed |
| Attach succeeds, then repeated `Failed to attach` and `not available on host` | The first module re-enumerated every few seconds. Replacing the module resolved it; the cause (firmware boot loop or hardware fault) was not determined. Try download mode before replacing |
| CMake: `esptool>=5.0.2 not found in PATH` | Run `west packages pip --install` in the active venv |
| VS Code: *the description can't be converted into a problem matcher* for `{"base": "$gcc", ...}` | `$gcc` is contributed by the C/C++ extension and cannot be used as `base`; use `"problemMatcher": "$gcc"` |
| VS Code: Ctrl+click on `#include <zephyr/...>` does nothing | The C/C++ extension was not installed in WSL. Install it for **WSL: Ubuntu**, select the `Zephyr ESP32-S3` configuration, build once and reload the window |
| Kconfig: *MBEDTLS ... has direct dependencies 0 with value n, but is currently being y-selected* and *Aborting due to Kconfig warnings* | `mbedtls` module missing; extend the project filter (Part 5.1) |
| CMake: *add_subdirectory given source ".../mbedtls/tf-psa-crypto" which is not an existing directory* | `tf-psa-crypto` module missing; extend the project filter (Part 5.1) |
| CMake: *'protoc' not found* or nanopb generator errors | Install `protobuf-compiler` and `pip install protobuf grpcio-tools` in the workspace venv (Part 5.3) |
| Link: *undefined reference to `z_impl_k_event_post`* | `CONFIG_EVENTS=y` missing in `prj.conf` |
| zephyr-utilities reports *"The environment changed since selection"* | Intended guard after tool or environment changes: run **Analyze** again and update the build configuration |

## Open items

- Commit the board definition and `zero_blink` to the agreed repository and record the decision if the ESP32-S3-Zero becomes a supported controller variant.
- Verify Wi-Fi connection and UDP delivery on the device; record rate, jitter and loss at 200 Hz with the test receiver.
- Verify the MPU-6050 wiring (GPIO1 SDA, GPIO2 SCL, GPIO4 INT) on hardware and move sampling to the data-ready interrupt.
- Decide whether device builds use Zephyr's nanopb module or the nanopb 0.4.9.1 pinned by the contract checks.
- Run the same steps for the recommended ESP32-S3-DevKitC-1-N8R8, which has an upstream Zephyr board.
