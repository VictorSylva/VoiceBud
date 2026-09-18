# Run VoiceBud on Windows or macOS

VoiceBud is a fully offline dictation and audio file transcription app for **Windows** and **macOS**.
- Real-time dictation at the cursor with `ctrl+shift`.
- Audio file upload and transcription via GUI or CLI.
- No cloud, no subscription. Everything runs locally on your machine.

---

## 🪟 Windows Setup Guide

### 1. Prerequisites
- **Python**: Python 3.10 to 3.14 (ensure *"Add Python to PATH"* was checked during installation).
- **Ollama** *(Optional, for LLM filler-word cleanup)*:
  - Download and run the installer from [ollama.com/download/windows](https://ollama.com/download/windows).
  - Open PowerShell / Command Prompt and pull the cleanup model:
    ```powershell
    ollama pull qwen3:4b-instruct
    ```
  *(Note: If Ollama is not installed or running, VoiceBud automatically falls back to raw transcripts without failing).*

### 2. Set up the project

Open PowerShell or Command Prompt in the project folder (`VoiceBud`):

```powershell
# Create a virtual environment
python -m venv .venv

# Activate it (PowerShell)
.\.venv\Scripts\Activate.ps1
# (Or in standard Command Prompt cmd.exe):
# .\.venv\Scripts\activate.bat

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run VoiceBud

```powershell
python main.py
```
- A purple microphone tray icon (`🎙️`) appears in your Windows system tray (bottom-right taskbar, next to the clock).
- The Whisper speech recognition model (`tiny.en`, ~75 MB) downloads automatically on first run.

### 4. How to Use

#### A. Real-Time Voice Dictation
1. Click into any text field (Notepad, browser, Word, Discord, etc.).
2. Press **`ctrl+shift`** → a floating purple waveform pill appears at the bottom of your screen.
3. Speak naturally (filler words like "um" and "uh" get cleaned up).
4. Press **`ctrl+shift`** again → the cleaned text is instantly pasted at your cursor.

#### B. Upload & Transcribe Audio Files (GUI)
1. Right-click the **`🎙️`** icon in your system tray (bottom-right taskbar).
2. Select **"Transcribe Audio File..."**.
3. Choose any audio file (`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.wma`, `.opus`).
4. The transcription window opens, showing:
   - Live transcription progress bar.
   - The full transcript in an editable text box.
   - **"📋 Copy to Clipboard"** button.
   - **"💾 Save as .txt..."** button.
   - **"✨ Clean with LLM" / "↺ Show Raw"** toggle button.

#### C. Batch Transcribe via Command Line (CLI)
You can also transcribe files directly from your terminal without opening the GUI:
```powershell
# Basic file transcription
python main.py -f "path\to\recording.mp3"

# Transcribe and copy result directly to your clipboard
python main.py -f "recording.mp3" -c

# Transcribe and save output to a text file
python main.py -f "recording.mp3" -o "transcript.txt"

# Transcribe with Ollama cleanup applied
python main.py -f "recording.mp3" --clean
```

### 5. Run Without Opening an Editor / Terminal

You have several ways to run VoiceBud without keeping an editor or terminal open:

#### Option A: Desktop Shortcut (Double-click to start anytime)
Generate a shortcut on your Desktop:
```powershell
.\.venv\Scripts\python.exe create_desktop_shortcut.py
```
- A **VoiceBud** shortcut is created on your Desktop.
- Double-clicking it launches VoiceBud silently into the system tray using `pythonw.exe` (no black terminal window).

#### Option B: Launch Silently via File Explorer
In the `VoiceBud` folder, you can simply double-click:
- **`start_voicebud.vbs`** (completely silent, zero window flash)
- or **`start_voicebud.bat`**

#### Option C: Start Automatically with Windows (Recommended for daily use)
To make VoiceBud launch silently in the background every time you turn on or log into Windows:
```powershell
.\.venv\Scripts\python.exe setup_startup.py
```
To remove it from startup later:
```powershell
.\.venv\Scripts\python.exe setup_startup.py --remove
```
*(Once running in the background, you will see the `🎙️` icon in your system tray next to the clock. Press `ctrl+shift` anywhere to dictate. To exit, right-click the `🎙️` tray icon and select "Quit".)*

---

## 🍎 macOS Setup Guide

### 1. Prerequisites
```bash
# Install Python and Ollama via Homebrew
brew install python@3.12 ollama

# Start Ollama & pull the model
ollama serve &
ollama pull qwen3:4b-instruct
```

### 2. Set up & Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3. Permissions on macOS
In **System Settings → Privacy & Security**, grant your Terminal:
- **Input Monitoring** (for global hotkey)
- **Accessibility** (to paste text)
- **Microphone** (prompted on first recording)

---

## ⚙️ Customization (`config.yaml`)

Edit `config.yaml` to customize your experience:
- **Hotkey (`hotkey.key`)**: e.g., `ctrl+shift`, `ctrl+alt`, `alt_r`, `ctrl_r`.
- **Mode (`hotkey.mode`)**:
  - `toggle`: Press once to start recording, press again to stop (default).
  - `hold`: Hold the keys while speaking, release to stop.
- **Speech Model (`stt.model`)**:
  - `tiny.en` (fastest, lowest CPU usage, ~75 MB)
  - `base` (~140 MB)
  - `small` (~460 MB)
  - `medium` (~1.5 GB)
- **Injection Method (`inject.method`)**:
  - `paste`: Synthesizes `Ctrl+V` (fastest, preserves clipboard).
  - `type`: Types each character directly using keyboard simulation.
- **LLM Cleanup (`llm.enabled`)**: Set to `false` if you only want raw speech recognition without Ollama.
