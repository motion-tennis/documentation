# Webcam and pose-estimation reference stack

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Tracking behavior](tracking.md) · [Hardware](hardware.md)

**Status:** proposed implementation stack based on the requested webcam-first direction. The user reports a Windows laptop with an RTX 5080 and is considering an Elgato Facecam or an alternative. Exact webcam generation, laptop GPU configuration, driver/runtime compatibility and achieved performance are not established. No package, model or camera has been installed or benchmarked by this documentation work.

## Recommended baseline

Use a USB webcam at a verified 1920 × 1080, 60 frames/s mode, native Windows capture, and **RTMO-m with 640 × 640 input**. Keep capture, inference and game rendering separately scheduled. Start with four separated play lanes and calibrated 2.5D mapping; defer unconstrained metric 3D racket position to a verified depth or multi-view phase.

| Planned module | Device and implementation boundary | Output |
| --- | --- | --- |
| Capture adapter | Windows laptop; C++ Media Foundation source reader and calibrated undistortion | Frame ID, raw source/driver timestamp, host QPC arrival, rectified image with `K_rect`, one-slot shared image buffer |
| Inference worker | Windows laptop; Python, RTMO-m via rtmlib and verified ONNX Runtime CUDA provider | COCO 17 image-space keypoints and scores; preprocessing metadata and inference timing |
| Person association | Tracking worker; bounded assignment from box/joint continuity | Session-scoped person IDs and explicit ambiguous/lost states |
| Publisher | Tracking worker; generated Protobuf encoder and bounded UDP sender | Per-person `skeleton_frame`, common-frame `frame_status`, trace records |
| Fusion consumer | Raspberry Pi 3 Model B; physics component | Historical IMU alignment, calibrated plane estimate, orientation replay and eligibility |

These module names are architectural boundaries, not current files or executable commands. The capture adapter should not wait for Python inference, network output or the game UI. It undistorts once using versioned camera calibration; the worker letterboxes the resulting rectified image, then the publisher reverses letterboxing and normalizes to that rectified image's original width/height. The Pi uses the calibration's `K_rect` and must not undistort again. Preserve raw distorted-frame representation and original timestamps separately if optional debug recording is enabled. The worker uses the newest waiting image; debug video recording must be independently buffered and disabled when its overhead is not characterized.

## Model choice and alternatives

The [official RTMO project](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmo) describes one-stage multi-person pose estimation without a separate human detector. This is a useful reference for four people because a top-down detector-plus-pose pipeline adds per-person work. Its published benchmark numbers use other hardware and must not be copied as RTX 5080 laptop results.

The initial model candidate is the RTMO-m body7 640 × 640 ONNX export named `rtmo-m_16xb16-600e_body7-640x640-39e78cc4_20231211.zip` in the [rtmlib adapter's balanced RTMO mapping](https://github.com/Tau-J/rtmlib/blob/main/rtmlib/tools/solution/body.py). Record the chosen artifact URL, local checksum, model metadata and notices before accepting it. The filename's short digest is not a substitute for a verified full artifact checksum.

| Candidate | Role in this plan | Limit or decision gate |
| --- | --- | --- |
| RTMO-m | Primary reference candidate | Measure four-person keypoint quality and full pipeline age on the actual laptop |
| RTMO-s or RTMO-l | Controlled speed/quality comparison | Change only through a recorded profile; never silently reduce quality to meet a deadline |
| RTMPose plus person detector | Comparison if wrist quality justifies added work | Benchmark the detector plus all four pose crops, not one crop alone |
| MediaPipe Pose Landmarker | Optional independent baseline | Configurable pose count is available, but four-person identity and quality still require testing; hip-relative world landmarks do not establish shared camera/world depth |
| Ultralytics pose models | Alternative requiring separate licensing review | Current vendor distribution uses AGPL-3.0 or Enterprise terms; do not assume the project's MIT license covers dependency/model obligations |

[rtmlib](https://github.com/Tau-J/rtmlib) supports inference without MMPose/MMCV dependencies, reducing the initial Windows build burden. Its code and [MMPose code](https://github.com/open-mmlab/mmpose/blob/main/LICENSE) use Apache-2.0; check selected model artifacts and associated notices separately. [MediaPipe's official guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python) documents configurable pose count, relative landmark outputs and skipped frames when live inference is busy. [Ultralytics documents its licensing choices](https://www.ultralytics.com/license).

## Windows and RTX 5080 compatibility gate

Do not assume that an old CUDA wheel runs correctly merely because a GPU is present. [NVIDIA's capability table](https://developer.nvidia.com/cuda/gpus) lists the RTX 5080 family at compute capability 12.0. [NVIDIA's Blackwell guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/index.html) explains that binaries need compatible native GPU code or forward-compatible PTX. Verify the actual laptop adapter, memory, driver, power mode and thermal behavior; a desktop benchmark or a product family name is insufficient.

The proposed runtime starts with ONNX Runtime's CUDA execution provider. Use the [official CUDA dependency matrix](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html) to choose matching CUDA/cuDNN/runtime versions and test the selected model. Reject silent CPU fallback and record operator placement. Windows runtime prerequisites are documented in the [official installation guide](https://onnxruntime.ai/docs/install/). No version combination is claimed tested here.

A reproducible runtime manifest must pin the Windows build, GPU/driver, Python, rtmlib revision, ONNX Runtime package, CUDA/cuDNN libraries, model checksum, preprocessing and postprocessing settings. Capture the actual execution providers, warm-up policy, batch size, GPU memory use and power profile. An ONNX export is not evidence that every operator uses the GPU.

TensorRT is an optional optimization after the baseline works. Build and validate an engine on the intended deployment profile, compare keypoints numerically with the reference model, and repeat timing tests. Serialized engines have platform and hardware compatibility constraints; do not distribute an arbitrary Linux-built engine to Windows. See [TensorRT's support matrix](https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/support-matrix.html).

## Camera selection and commissioning

An Elgato product-family name is not an exact model. Verify the label, generation, firmware and supported UVC modes before buying additional hardware or writing a dependency lock.

| Camera candidate | Verified manufacturer information | Project consequence |
| --- | --- | --- |
| Facecam / Facecam MK.2 | 1080p60; fixed focus published as 30–120 cm | Do not assume four full-body people several metres away are sharp; validate at the actual room distance or choose another model |
| Facecam 4K operated at 1080p60 | The detailed technical sheet lists 25 cm to infinity focus at 1080p, with 30–120 cm stated for 4K | Stronger named room-distance candidate, still subject to four-person sharpness, exposure, field-of-view and latency tests |
| Another webcam meeting the profile | Sustained 1080p60, documented room-distance focus, fixed/repeatable framing and usable exposure controls | Accept by measured capture age and pose quality, not resolution or AI marketing alone |

Sources: [Facecam/MK.2 manufacturer specifications](https://www.elgato.com/ww/en/p/facecam-mk2), [Facecam 4K detailed specifications](https://www.elgato.com/us/en/explorer/products/camera/facecam-4k-tech-specs/). The differing focus ranges are mode-specific; do not apply the 1080p claim to 4K operation. No camera purchase or successful room-scale test is implied.

Use a direct suitable USB port and record negotiated format and frame rate. Prefer a measured low-delay uncompressed mode when available; compressed transport adds decoder and buffering behavior that must be measured. Disable HDR, automatic reframing, background effects, digital zoom changes and variable frame-rate processing for the initial timing profile. Lock exposure/white balance and focus where the chosen camera supports it after setting up the actual lighting. Any change invalidating calibration requires a new calibration ID.

Place the camera so all four players' required joints remain visible throughout the declared swing envelope. Verify actual horizontal/vertical coverage rather than treating a quoted diagonal FOV as usable court width. Check hand pixel size, motion blur, focus and occlusion at near/far lane edges. The GPU cannot reconstruct missing detail from a blurred or occluded hand with measured certainty. Camera-to-player distances, lane spacing and swing-clearance geometry must be recorded from the actual room rather than assumed from a desk-camera specification.

## Capture timestamps and latency

[Microsoft documents `IMFSample::GetSampleTime`](https://learn.microsoft.com/en-us/windows/win32/api/mfobjects/nf-mfobjects-imfsample-getsampletime) as presentation time in 100 ns units. [The device-timestamp attribute](https://learn.microsoft.com/en-us/windows/win32/medfound/mfsampleextension-devicetimestamp) uses a driver timestamp in a QPC-related epoch. Preserve the raw value, kind, domain and conversion; neither API name alone proves the exact exposure instant. An OpenCV read-return time is host receipt, not a substitute for optical capture time.

[Media Foundation's low-latency setting](https://learn.microsoft.com/en-us/windows/win32/medfound/mf-low-latency) is a useful capture configuration option, not a deadline guarantee. Measure frame delivery and buffering with a controlled flashing LED/common reference. The reference profile requires exposure-to-timestamp uncertainty no greater than 8 ms; if it cannot be established, report unknown acquisition age and fail the bounded-freshness acceptance gate instead of manufacturing a camera timestamp.

Log capture/driver time, host arrival, inference start/end, association completion, send and Pi arrival separately. GPU inference duration alone excludes sensor exposure, USB delivery, frame selection, preprocessing and queueing. Keep the camera-rate target, pose-rate target, pose age and controller application RTT as separate metrics. The limits and uncertainty rules are in [tracking](tracking.md) and [timing](timing.md).

## True 3D upgrade gate

Single-view image observations define camera rays. A plane constraint supplies a gameplay model; it does not measure arbitrary physical depth. This follows from the [calibrated projective camera model](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html). A learned hip-relative 3D pose also does not by itself establish a shared metric court frame.

A later true-3D profile must select and validate a depth or calibrated multi-view sensor arrangement, synchronize exposures as required, establish a metric world transform, measure occlusion/error behavior, and introduce an explicit protocol representation for depth-backed joints. Kinect v2 remains a possible separate adapter, with a verified skeleton backend and compatible host. `libfreenect2` supplies sensor access/registration, not body tracking by itself; see the [upstream project](https://github.com/OpenKinect/libfreenect2). Do not label the first 2.5D release as measured 3D tracking.

## Implementation and acceptance order

1. Identify the exact camera and prove four-person field coverage, focus and stable capture mode.
2. Build the timestamp-preserving capture adapter and latest-only handoff; measure exposure/driver uncertainty.
3. Lock and verify the GPU inference environment and RTMO-m artifact; test GPU placement and four-person throughput under game-render load.
4. Implement identity association and guided controller pairing; reject crossings/occlusions that cannot be resolved reliably.
5. Integrate per-person pose packets with Pi history, plane calibration and historical IMU alignment.
6. Run the complete [test matrix](testing.md), export the [debug traces](debugging.md), and record useful-input rate, failure reasons, frame-age tails and all skipped frames.

Do not publish working install or launch commands until the corresponding files and supported environment exist in `motion-tennis-camera-tracking`.
