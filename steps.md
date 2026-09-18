# 🎙️ VoiceBud — The Prompts That Built It

VoiceBud is a fully offline, privacy-first desktop voice dictation and audio transcription application for **Windows and macOS**.

This document describes how to recreate and evolve VoiceBud using **Antigravity** from a clean repository.

The prompts are intentionally written as a sequence rather than one enormous prompt. Each stage establishes a working foundation, verifies it, and then adds another capability without breaking what already works.

The goal is not simply to generate code. The goal is to have Antigravity **inspect, implement, run, verify, diagnose, and fix** the application at every stage.

---

## What VoiceBud Is

VoiceBud is a local alternative to cloud-based voice dictation tools such as Wispr Flow.

It provides:

* System-wide voice dictation
* Global configurable hotkeys
* Toggle and hold-to-talk modes
* Local Whisper-based speech recognition
* Local LLM transcript cleanup through Ollama
* Filler-word removal
* Punctuation and capitalization correction
* Minor grammar correction without rewriting the user's meaning
* Clipboard-preserving text injection
* A real-time recording waveform
* Windows system-tray integration
* macOS menu-bar integration
* Audio-file transcription
* Raw/cleaned transcript switching
* Editable transcription output
* Copy-to-clipboard functionality
* `.txt` export
* Batch CLI transcription
* Background startup
* Windows and macOS support
* No cloud speech APIs
* No telemetry
* No subscription requirement

The architecture should remain **local-first and modular**, allowing individual components such as Whisper models and cleanup models to be changed without rewriting the application.

---

# How To Recreate VoiceBud

Give the following prompts to Antigravity **in order**.

Do not skip directly to later prompts unless the earlier functionality has already been verified.

The most important rule throughout the build is:

> **Never sacrifice an already-working feature in order to implement a new one.**

Before every major change, Antigravity should inspect the existing implementation and understand how the relevant modules interact.

---

# Prompt 1 — Main Architecture and Working MVP

## Objective

Build the first complete working version of VoiceBud.

Give this prompt to Antigravity:

```text
Build a production-quality desktop application called VoiceBud.

VoiceBud is a fully offline, privacy-first voice dictation and audio transcription application for Windows and macOS.

IMPORTANT DEVELOPMENT RULES

1. First inspect the entire repository and understand the existing project before modifying anything.
2. Do not blindly rewrite existing files.
3. Preserve any functionality that is already working.
4. Keep the architecture modular.
5. Do not introduce unnecessary frameworks or dependencies.
6. Prefer mature Python libraries with good Windows/macOS support.
7. The application must work without internet access after its dependencies and local models have been installed.
8. Never send microphone audio or transcripts to a cloud API.
9. Do not add telemetry or analytics.
10. Do not hardcode configuration values that should be configurable.
11. After implementation, actually run the application and test the important workflows.
12. If something fails, diagnose the actual error and fix it instead of simply reporting it.
13. Do not stop at "the code looks correct". Prove the application works.

CORE PRODUCT

VoiceBud should provide two major capabilities:

A. REAL-TIME SYSTEM-WIDE DICTATION

The user should be able to:

1. Focus any text field in any application.
2. Press a configurable global hotkey.
3. VoiceBud starts recording.
4. A recording indicator/waveform appears.
5. The user speaks.
6. The user presses the hotkey again in toggle mode, or releases the hotkey in hold mode.
7. VoiceBud transcribes the audio locally.
8. VoiceBud optionally cleans the transcript using a local LLM.
9. The cleaned text is inserted at the current cursor position.

It should work in applications such as:

- Notepad
- Microsoft Word
- Google Docs
- Chrome
- Edge
- VS Code
- Slack
- Discord
- Terminal
- Other normal text-input fields

B. AUDIO FILE TRANSCRIPTION

The application should also allow the user to select an audio file and transcribe it locally.

Support at minimum:

- WAV
- MP3
- M4A
- FLAC
- OGG
- AAC
- OPUS

The file transcription interface should eventually support:

- transcription progress
- raw transcript
- cleaned transcript
- editable output
- copy to clipboard
- save transcript as TXT

TECH STACK

Use Python.

Speech-to-text:

- faster-whisper
- CTranslate2
- Silero VAD through faster-whisper's VAD support

Audio:

- sounddevice
- numpy

Local LLM cleanup:

- Ollama

Recommended default model:

qwen3:4b-instruct

Do NOT use the plain qwen3:4b model as the default cleanup model.

Text injection:

- pyperclip where appropriate
- platform-specific keyboard/input APIs
- Windows input APIs where required
- macOS Quartz/PyObjC where required

System integration:

- Windows system tray
- macOS menu bar

GUI:

Use a lightweight Python GUI approach such as Tkinter unless the existing project already has a better working implementation.

Do not introduce Electron.

Do not introduce a browser-based frontend.

CONFIGURATION

Create a central configuration system.

At minimum support:

hotkey:
    key/chord configuration
    mode: toggle | hold

stt:
    model
    language
    device
    compute type
    VAD settings

llm:
    enabled
    model
    base_url
    temperature
    system_prompt

audio:
    sample rate
    channels
    pre-roll duration

injection:
    method
    fallback

The LLM model must never be hardcoded inside the cleanup implementation.

Changing:

llm.model

should be enough to change the cleanup model.

STT MODEL

Default to a lightweight model appropriate for local CPU inference.

Make the model configurable so the user can select larger models when their hardware allows it.

Support the architecture needed for models such as:

- tiny
- base
- small
- medium
- large-v3

Do not force users to download a huge model during initial setup.

AUDIO PRE-ROLL

Implement a short circular microphone buffer.

Use approximately 500 ms of pre-roll audio so that the first syllable of a sentence is not lost when recording starts.

TRANSCRIPT CLEANUP

The LLM must NOT rewrite the user's speech.

Its job is limited to:

- removing filler words
- removing obvious verbal stumbles
- correcting capitalization
- correcting punctuation
- correcting very small grammar mistakes

It must NOT:

- summarize
- answer questions contained in the transcript
- translate
- add facts
- invent information
- change the user's intent
- change the user's tone unnecessarily
- turn speech into a different piece of writing

Use a low temperature around 0.1.

If the Ollama model is unavailable, VoiceBud must gracefully fall back to the raw Whisper transcript.

SHORT-UTTERANCE OPTIMIZATION

If a transcript is fewer than approximately 10 words, skip LLM cleanup and use the raw transcript.

This keeps short responses fast.

CLIPBOARD SAFETY

When injecting text:

1. Save the user's current clipboard.
2. Put the VoiceBud transcript into the clipboard.
3. Trigger the platform's paste action.
4. Wait enough time for the paste operation.
5. Restore the user's original clipboard.

Never permanently overwrite the user's clipboard.

PROJECT STRUCTURE

Use a clean modular structure.

For example:

main.py
config.py
config.yaml

audio.py
hotkey.py
transcribe.py
cleanup.py
inject.py

ui/
    ...

platform/
    windows.py
    macos.py

Do not create dozens of unnecessary files.

FIRST MILESTONE

After implementation:

1. Install dependencies.
2. Verify Python imports.
3. Verify the Whisper model can load.
4. Verify microphone capture.
5. Verify transcription.
6. Verify Ollama communication when available.
7. Verify cleanup.
8. Verify text injection.
9. Run one complete dictation workflow.
10. Test at least one audio-file transcription.

Fix any failures before declaring the milestone complete.

At the end, provide:

- what was implemented
- how to run it
- which files were created
- which features were actually tested
- any platform-specific setup still required
```

---

# Prompt 2 — Make VoiceBud a Real Desktop Application

Once the core dictation pipeline works:

```text
Now turn VoiceBud from a script into a proper desktop application.

IMPORTANT:

Do not rewrite the working transcription pipeline.

Do not remove any existing features.

First inspect the current implementation and identify the safest integration points.

Implement:

1. Windows system tray integration.

2. macOS menu-bar integration.

3. VoiceBud should continue running in the background after its main window is closed.

4. Add a tray/menu-bar icon.

5. Provide at minimum:

   - Start/Stop VoiceBud
   - Open Transcription
   - Settings if applicable
   - About
   - Quit

6. Display the currently configured hotkey in the menu.

7. Show an appropriate application name:

   VoiceBud

rather than generic names such as Python.

8. Make the application start without requiring a terminal window for normal users.

9. Make sure the background process does not terminate when the transcription GUI is closed.

10. Make sure only one VoiceBud background instance can run at a time.

11. Handle clean shutdown properly.

12. Test the tray/menu-bar lifecycle.

The application should now feel like a desktop utility rather than a Python script.

Do not package it into an installer yet.

First make the application lifecycle reliable.
```

---

# Prompt 3 — Global Hotkey System

```text
Improve VoiceBud's global hotkey system.

IMPORTANT:

Preserve the existing recording/transcription pipeline.

The hotkey system must work globally, not only when the VoiceBud window is focused.

Implement configurable hotkeys supporting:

1. Single keys where technically possible.

2. Multi-key chords such as:

   ctrl+shift

   ctrl+alt

   ctrl+shift+space

   etc.

3. Two operating modes:

   hotkey.mode = toggle

   and

   hotkey.mode = hold

TOGGLE MODE

Press once:

START recording.

Press again:

STOP recording.

HOLD MODE

Press and hold:

START recording.

Release:

STOP recording.

The hotkey configuration must come from configuration rather than being hardcoded.

Handle key-down and key-up events safely.

Prevent duplicate start/stop events.

Prevent recording from remaining active if a key event is lost.

Handle conflicts gracefully.

If the configured hotkey cannot be registered, show a clear error and suggest another key combination.

Default hotkey:

ctrl+shift

Do not use F5 as the default.

Do not claim that every possible keyboard key is available on every operating system. Respect platform limitations.

After implementation, test the hotkey from outside the VoiceBud application, including while another application is focused.
```

---

# Prompt 4 — Recording Waveform and Visual Feedback

```text
Add a professional recording indicator to VoiceBud.

Do not change the existing audio recording or transcription logic unless necessary.

When VoiceBud begins recording:

1. Display a small floating waveform/pill.

2. It should remain above normal application windows.

3. Position it near the bottom-center of the screen.

4. It should clearly communicate:

   VoiceBud is recording.

5. Animate the waveform using the REAL microphone amplitude.

6. The waveform should react to speech volume.

7. It must not simply be a fake looping animation.

8. When recording stops, remove or hide the indicator.

9. If recording fails, show an appropriate error state.

10. Do not block the user's active application.

11. Do not steal keyboard focus.

12. The overlay must work on supported Windows and macOS environments.

Use the existing GUI stack where possible.

Keep dependencies minimal.

Also provide an appropriate idle/processing state if useful, for example:

Recording
Processing
Transcribing
Cleaning
Done

The user should always know what VoiceBud is currently doing.
```

---

# Prompt 5 — Harden Local Whisper Transcription

```text
Now audit and improve the Whisper transcription pipeline.

Do not change the public behavior of VoiceBud.

Inspect:

- audio capture
- sample rate
- channel handling
- pre-roll buffer
- audio conversion
- Whisper model loading
- VAD
- language handling
- model/device configuration
- transcription errors
- empty recordings

Implement robust handling for:

1. Very short recordings.

2. Long recordings.

3. Silence.

4. No microphone available.

5. Microphone permission denied.

6. Whisper model missing.

7. Corrupted audio.

8. Unsupported audio formats.

9. Model loading failure.

10. User stopping a recording quickly.

Use VAD to reduce unnecessary silence processing.

Keep the 500 ms pre-roll behavior.

Make model configuration explicit.

Avoid loading the Whisper model repeatedly for every utterance.

Load/cache it appropriately so repeated dictation is fast.

If practical, make model loading lazy:

The application can start quickly, and the model loads when first required.

Add useful logging without logging private transcript content unnecessarily.

Test both live microphone transcription and audio-file transcription.
```

---

# Prompt 6 — Local LLM Cleanup That Does Not Rewrite the User

```text
Audit the VoiceBud LLM cleanup system.

The purpose of the LLM is transcript cleanup, NOT content generation.

The user's spoken meaning must be preserved.

The cleanup system should:

- remove filler words such as um, uh, ah, like, you know when they are clearly fillers
- remove obvious verbal stumbles
- fix punctuation
- fix capitalization
- correct obvious minor grammar errors

It must NOT:

- answer questions
- summarize
- expand ideas
- add information
- translate
- paraphrase unnecessarily
- rewrite the user's voice
- change names
- change numbers
- invent facts
- respond conversationally to the transcript

Use a strict system prompt.

Use temperature approximately 0.1.

Send think=false where supported by Ollama.

The configured model must come exclusively from:

llm.model

Do not hardcode a model name in cleanup.py.

Recommended default:

qwen3:4b-instruct

If Ollama is unavailable:

- do not crash
- use the raw transcript

If the configured model does not exist:

display a clear message such as:

Model X is not installed.
Run: ollama pull X

Then fall back to raw transcription.

Keep the cleanup pipeline asynchronous or otherwise non-blocking where practical so the GUI remains responsive.

Retest short utterances.

Anything under approximately 10 words should bypass the LLM.

Test examples where the transcript contains:

- fillers
- repeated words
- questions
- technical terms
- numbers
- names
- code-related speech

The final text must remain faithful to the original speech.
```

---

# Prompt 7 — Audio Transcription GUI

```text
Build the VoiceBud audio transcription dashboard.

Do not remove real-time dictation.

Add a proper desktop GUI accessible from the VoiceBud tray/menu-bar icon.

The interface should allow the user to:

1. Select an audio file.

2. Support:

   .wav
   .mp3
   .m4a
   .flac
   .ogg
   .aac
   .opus

3. Start transcription.

4. Show progress/status.

5. Display the raw Whisper transcript.

6. Display the cleaned transcript.

7. Toggle between:

   Raw
   Cleaned

8. Allow the user to edit the transcript.

9. Copy the result to the clipboard.

10. Save the result as a .txt file.

11. Start another transcription without restarting VoiceBud.

12. Handle errors gracefully.

The GUI should use a dark, professional desktop-tool aesthetic.

Do not make the GUI unnecessarily complicated.

The transcription engine should remain separate from the GUI so the same transcription functionality can be reused by the CLI.

Make sure large audio files do not freeze the entire interface.

Use background processing where appropriate.

Test with several supported formats.
```

---

# Prompt 8 — Batch CLI Mode

```text
Add a command-line interface to VoiceBud without breaking the desktop application.

The CLI must reuse the SAME transcription engine used by the GUI.

Do not duplicate the Whisper implementation.

Support a workflow such as:

python main.py -f meeting.mp3 -o transcript.txt --clean

Implement sensible options for:

-f / --file
-o / --output
-c / --clean
-m / --model
-l / --language

Where appropriate.

The CLI should:

1. Validate the input file.

2. Transcribe locally.

3. Optionally clean with Ollama.

4. Save the transcript.

5. Print useful progress.

6. Return appropriate exit codes on failure.

7. Never require the GUI.

8. Work without the tray application being open.

Do not send any audio or transcript to external APIs.

Document the CLI usage briefly.
```

---

# Prompt 9 — Windows Background Startup

```text
Now implement reliable Windows background deployment.

IMPORTANT:

Do not modify the working transcription engine.

VoiceBud should be able to run automatically when Windows starts.

The user should not need to manually open a terminal and run:

python main.py

Implement a reliable startup mechanism.

The normal background mode should:

- start VoiceBud at login
- run without opening a visible console window
- keep the system tray icon available
- keep global hotkeys active
- keep microphone recording available
- allow the user to quit VoiceBud from the tray

Use pythonw.exe or an appropriate Windows application-launch mechanism where suitable.

Do not install VoiceBud as a Windows service if that would interfere with interactive microphone/input permissions.

Provide a safe install/uninstall mechanism for startup.

Do not create duplicate startup entries.

Test:

1. Start VoiceBud manually.
2. Enable startup.
3. Restart/log out and back in.
4. Confirm VoiceBud starts.
5. Confirm tray icon appears.
6. Confirm global hotkey works.
7. Confirm dictation works.
```

---

# Prompt 10 — macOS Background Startup

```text
Now implement reliable macOS background startup.

Do not break Windows support.

VoiceBud should be able to run automatically when the user logs in.

Use a macOS LaunchAgent or an appropriate user-level launch mechanism.

Requirements:

- starts at login
- runs in the user's session
- remains available when Terminal or the editor is closed
- keeps the global hotkey active
- keeps microphone access available
- writes useful logs
- supports clean shutdown
- can be enabled/disabled

Do not run VoiceBud as a privileged system daemon.

Use the user's environment and virtual environment correctly.

Handle paths safely.

Do not assume the working directory is the repository directory.

Document macOS permissions required for:

- Microphone
- Accessibility
- Input Monitoring

If macOS permissions prevent functionality, show a useful diagnostic message.

Do not falsely claim that permissions can be automatically granted by the application.

Test the LaunchAgent lifecycle.
```

---

# Prompt 11 — Platform Abstraction and Cross-Platform Audit

```text
Perform a full Windows/macOS compatibility audit.

VoiceBud must remain one application with platform-specific implementations where required.

Inspect every use of:

- keyboard events
- clipboard
- paste
- system tray
- menu bar
- microphone
- filesystem paths
- startup
- process management
- GUI behavior

Move genuinely platform-specific behavior behind platform abstractions where appropriate.

For example:

platform/windows.py
platform/macos.py

Do not create abstractions merely for the sake of abstraction.

The goal is:

shared application logic
+
small platform-specific adapters.

Verify:

Windows:
- global hotkey
- microphone
- tray
- clipboard
- text injection
- background startup

macOS:
- global hotkey
- microphone
- menu bar
- clipboard
- text injection
- LaunchAgent
- Accessibility/Input Monitoring

Do not break either platform while fixing the other.

After the audit, run the application on the platform currently available and perform as much cross-platform static verification as possible for the other platform.
```

---

# Prompt 12 — Settings and Configuration

```text
Improve VoiceBud's configuration system.

The user should not have to edit Python source code to customize normal behavior.

Make the following configurable:

HOTKEY

- key/chord
- toggle/hold mode

STT

- Whisper model
- language
- device
- compute type
- VAD

AUDIO

- sample rate
- channels
- pre-roll

LLM

- enabled
- Ollama URL
- model
- temperature
- cleanup prompt

INJECTION

- primary method
- fallback method

APPLICATION

- startup enabled/disabled
- logging level where appropriate

Maintain sensible defaults.

Do not expose dangerous or unnecessary technical settings to normal users unless needed.

Validate configuration values before starting.

If configuration is invalid:

- show the problem
- explain the expected value
- fall back safely where possible

Never silently use an unexpected configuration.

Make model switching easy.

For example:

llm:
  model: qwen3:4b-instruct

Changing that value should be enough to switch the cleanup model.
```

---

# Prompt 13 — Reliability, Error Handling and Recovery

```text
Perform a reliability audit of the entire VoiceBud application.

Do not add features.

Instead, try to break the application.

Test:

1. Microphone unavailable.
2. Microphone permission denied.
3. Ollama not running.
4. Ollama model missing.
5. Whisper model missing.
6. Invalid configuration.
7. Empty recording.
8. Extremely short recording.
9. Long recording.
10. Silence.
11. Unsupported audio file.
12. Corrupted audio.
13. Clipboard unavailable.
14. Text injection failure.
15. Global hotkey conflict.
16. Multiple VoiceBud instances.
17. GUI closed while transcription is running.
18. Application shutdown while recording.
19. User presses the hotkey rapidly several times.
20. Ollama becomes unavailable during cleanup.

For each failure:

- do not crash unnecessarily
- show a useful user-facing message
- log technical details where appropriate
- recover automatically when safe
- fall back to raw transcription when LLM cleanup fails

Pay special attention to race conditions around:

- recording state
- hotkey state
- transcription
- GUI updates
- clipboard restoration
- shutdown

After the audit, run a complete end-to-end dictation test.
```

---

# Prompt 14 — Performance and Latency Optimization

```text
Now optimize VoiceBud for practical local performance.

Do not sacrifice transcription accuracy or reliability simply to produce an artificial benchmark.

Measure the actual pipeline:

hotkey
→ recording
→ transcription
→ cleanup
→ injection

Identify the largest sources of latency.

Optimize:

1. Whisper model loading.

2. Repeated model initialization.

3. Audio buffering.

4. VAD.

5. Short utterances.

6. Ollama requests.

7. Clipboard injection.

8. GUI rendering.

9. Background processing.

Do not send short utterances through the LLM.

Keep the pre-roll buffer.

Avoid blocking the UI.

Reuse loaded models.

Where possible, make model selection hardware-aware without making the application overly complicated.

Document realistic performance expectations rather than promising a fixed latency.

Do not claim "sub-second" performance unless the actual test demonstrates it on the target machine.
```

---

# Prompt 15 — Security and Privacy Audit

```text
Perform a privacy and security audit of VoiceBud.

The core requirement is:

VoiceBud must operate locally.

Verify that microphone audio and transcripts are not sent to cloud APIs.

Search the entire codebase for:

- HTTP requests
- cloud SDKs
- telemetry
- analytics
- tracking
- unexpected external network calls
- hardcoded API keys
- credentials
- unnecessary logging of transcript content

Ollama's local endpoint is allowed.

Do not remove Ollama support.

Ensure:

- no API secrets are hardcoded
- user transcripts are not unnecessarily written to disk
- temporary audio files are cleaned up where applicable
- logs do not unnecessarily contain sensitive speech
- clipboard contents are restored
- files selected for transcription remain local

If any network dependency exists, document exactly why it exists.

The final application should be accurately described as local/offline after models and dependencies have been installed.
```

---

# Prompt 16 — Final UX and Product Polish

```text
Now perform a product-quality review of VoiceBud.

Do not redesign the entire application.

Improve obvious usability problems.

Review:

- application naming
- tray/menu-bar experience
- recording indicator
- transcription dashboard
- error messages
- loading states
- empty states
- button labels
- keyboard shortcuts
- status messages
- dark-mode appearance
- spacing
- typography
- accessibility
- consistency

The application should feel like a focused desktop utility.

Avoid unnecessary animations.

Avoid unnecessary configuration screens.

Avoid visual clutter.

The primary experience should remain:

Press hotkey
→ Speak
→ Stop
→ Text appears.

The secondary experience should remain:

Open VoiceBud
→ Select audio file
→ Transcribe
→ Review/edit
→ Copy or save.
```

---

# Prompt 17 — Final Production Audit

```text
This is the final production audit.

Do not add new features unless they are required to fix a real issue.

Inspect the entire VoiceBud repository.

Verify that:

- the application starts
- the tray/menu-bar integration works
- global hotkey works
- toggle mode works
- hold mode works
- recording works
- pre-roll works
- waveform works
- Whisper transcription works
- Ollama cleanup works
- raw fallback works
- short utterance bypass works
- clipboard is preserved
- text injection works
- file transcription works
- GUI editing works
- copy works
- TXT export works
- CLI works
- Windows startup works
- macOS startup works
- configuration works
- errors are handled
- duplicate instances are prevented
- shutdown is clean

Then inspect dependencies.

Remove dependencies that are not actually used.

Check for:

- dead code
- duplicate implementations
- unused imports
- hardcoded configuration
- platform-specific code leaking into shared modules
- misleading comments
- stale documentation
- debug prints
- temporary files
- development-only behavior

Do not make speculative changes.

After the audit, run the most important end-to-end workflow:

1. Start VoiceBud.
2. Focus a text editor.
3. Trigger the global hotkey.
4. Record speech.
5. Stop recording.
6. Transcribe.
7. Clean if enabled.
8. Inject the text.
9. Verify the text is correct.

Then test one audio file.

Only after these workflows work should you declare VoiceBud ready.
```

---

# Final Architecture

The resulting application should conceptually follow this pipeline:

```text
                    ┌─────────────────────┐
                    │      VoiceBud       │
                    │   Desktop Utility   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
      Real-Time Dictation                Audio File Mode
              │                                 │
              ▼                                 ▼
        Global Hotkey                     File Selector
              │                                 │
              ▼                                 ▼
       Audio Recorder                    Audio Decoder
              │                                 │
              └──────────────┬──────────────────┘
                             ▼
                      Audio Processing
                             │
                      16 kHz / Mono
                             │
                       Pre-roll + VAD
                             │
                             ▼
                     faster-whisper
                             │
                             ▼
                       Raw Transcript
                             │
                  ┌──────────┴──────────┐
                  │                     │
            < 10 words              >= 10 words
                  │                     │
                  │                     ▼
                  │                 Ollama
                  │                     │
                  │                     ▼
                  │               Cleaned Text
                  │                     │
                  └──────────┬──────────┘
                             ▼
                     Transcript Result
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       Real-Time Mode                 File Mode
              │                             │
              ▼                             ▼
       Clipboard + Input             GUI Editor
              │                             │
              ▼                             ├── Copy
       Focused Application               └── Save TXT
```

---

# Recommended Core Modules

A clean implementation can use a structure similar to:

```text
VoiceBud/
│
├── main.py
├── config.py
├── config.yaml
├── requirements.txt
│
├── audio.py
├── hotkey.py
├── transcribe.py
├── cleanup.py
├── inject.py
│
├── cli.py
│
├── ui/
│   ├── tray.py
│   ├── waveform.py
│   └── transcriber.py
│
├── platform/
│   ├── windows.py
│   └── macos.py
│
├── startup/
│   ├── windows.py
│   └── macos.py
│
└── README.md
```

The exact structure does not need to match this perfectly.

The important architectural principle is:

**shared functionality should remain shared, while operating-system-specific behavior should be isolated.**

---

# VoiceBud's Core Design Principles

These principles should survive future development.

### 1. Local First

VoiceBud should process speech locally.

No cloud transcription is required.

### 2. User's Words Stay The User's Words

The LLM is a cleanup layer, not a writing assistant.

VoiceBud should improve readability without changing meaning.

### 3. Fast Path First

Short utterances should avoid unnecessary processing.

### 4. Graceful Degradation

If Ollama fails, transcription should still work.

If cleanup fails, raw transcription should still be available.

### 5. Platform Native Where Necessary

Windows and macOS can share the core engine while using different mechanisms for:

* global input
* text injection
* tray/menu bar
* startup
* permissions

### 6. Configuration Over Hardcoding

Models, hotkeys, modes, and other user-adjustable behavior should come from configuration.

### 7. Never Break Existing Functionality

Every upgrade should preserve previously working workflows.

### 8. Verify, Don't Assume

Antigravity should run the application and test the feature it just implemented.

A feature is not considered complete merely because the code compiles.

---

# Final User Experience

The primary VoiceBud workflow should feel like this:

```text
User is typing anywhere
        ↓
Press Ctrl + Shift
        ↓
VoiceBud recording indicator appears
        ↓
User speaks naturally
        ↓
Press Ctrl + Shift again
        ↓
Local Whisper transcription
        ↓
Short speech?
   ┌────┴────┐
   │         │
  Yes       No
   │         │
   │      Local Ollama
   │         │
   └────┬────┘
        ↓
Clean transcript
        ↓
Clipboard safely preserved
        ↓
Text inserted at cursor
```

For audio files:

```text
Open VoiceBud
      ↓
Select audio file
      ↓
Local Whisper transcription
      ↓
Raw transcript
      ↓
Optional Ollama cleanup
      ↓
Edit transcript
      ↓
Copy / Save TXT
```

The result should be a **free, local, cross-platform desktop voice tool** that provides the convenience of modern AI dictation without requiring a cloud subscription or sending the user's voice to an external service.
