"""VoiceBud: hold or toggle your hotkey to dictate anywhere. Fully offline.
Also supports batch transcribing audio files via GUI window or CLI.

Windows Setup:
  python -m venv .venv
  .\\.venv\\Scripts\\pip install -r requirements.txt
  ollama serve   (in another terminal, if using LLM cleanup)
  .\\.venv\\Scripts\\python main.py
"""
import argparse
import os
import signal
import sys
import threading
import time

import yaml

import inject
from audio import Recorder
from cleanup import Cleaner
from hotkey import PushToTalk
from overlay import Overlay
from transcribe import Transcriber
from transcribe_window import TranscribeWindow

APP_NAME = "VoiceBud"
IS_MACOS = sys.platform == "darwin"


def check_permissions():
    """macOS permission probes; no-op on Windows."""
    if not IS_MACOS:
        return
    try:
        import Quartz
        msgs = []
        try:
            if not Quartz.CGPreflightListenEventAccess():
                msgs.append("Input Monitoring (for the global hotkey)")
        except AttributeError:
            pass
        try:
            from ApplicationServices import AXIsProcessTrusted
            if not AXIsProcessTrusted():
                msgs.append("Accessibility (to paste text into other apps)")
        except Exception:
            pass
        if msgs:
            print("SETUP NEEDED — grant your terminal these permissions in")
            print("System Settings -> Privacy & Security, then restart this app:")
            for m in msgs:
                print(f"  - {m}")
            print("  - Microphone (macOS will prompt on first recording)")
    except ImportError:
        pass


def rename_app():
    """Best-effort: show 'VoiceBud' instead of 'Python' on macOS."""
    if not IS_MACOS:
        return
    try:
        from Foundation import NSBundle, NSProcessInfo
        NSProcessInfo.processInfo().setProcessName_(APP_NAME)
        info = NSBundle.mainBundle().infoDictionary()
        if info is not None:
            info["CFBundleName"] = APP_NAME
    except Exception:
        pass


def create_windows_tray(hotkey_str, on_transcribe, on_quit):
    """Create a system tray icon for Windows / Linux using pystray."""
    try:
        import pystray
        from PIL import Image, ImageDraw

        # 64x64 purple circle with white microphone icon
        img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((4, 4, 60, 60), fill=(163, 107, 255, 255))
        d.rounded_rectangle((24, 14, 40, 36), radius=8, fill=(255, 255, 255, 255))
        d.arc((18, 24, 46, 44), start=0, end=180, fill=(255, 255, 255, 255), width=3)
        d.line((32, 44, 32, 52), fill=(255, 255, 255, 255), width=3)
        d.line((24, 52, 40, 52), fill=(255, 255, 255, 255), width=3)

        menu = pystray.Menu(
            pystray.MenuItem(f"{APP_NAME} — press {hotkey_str} to dictate", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Transcribe Audio File...", on_transcribe),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Quit {APP_NAME}", on_quit),
        )
        return pystray.Icon("VoiceBud", img, APP_NAME, menu)
    except Exception as e:
        print(f"(System tray icon note: {e})")
        return None


def run_cli_file_transcription(file_path, output_path=None, copy_to_clipboard=False, run_clean=False):
    """Direct CLI batch transcription without launching the background tray app."""
    if not os.path.exists(file_path):
        print(f"Error: Audio file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    print(f"Loading STT model ({cfg['stt']['model']})...")
    stt = Transcriber(cfg["stt"])
    cleaner = Cleaner(cfg["llm"]) if run_clean or cfg.get("llm", {}).get("enabled", False) else None

    print(f"Transcribing '{os.path.basename(file_path)}'...")
    t0 = time.time()

    def progress(frac, text):
        pct = int(frac * 100)
        sys.stdout.write(f"\rProgress: {pct}%")
        sys.stdout.flush()

    raw_text = stt.transcribe(file_path, progress_callback=progress)
    print()  # newline after progress
    print(f"Transcription finished in {time.time() - t0:.2f}s.")

    final_text = raw_text
    if run_clean and cleaner and cleaner.enabled:
        print(f"Cleaning transcript with Ollama ({cfg['llm']['model']})...")
        t_clean = time.time()
        final_text = cleaner.clean(raw_text)
        print(f"Cleanup finished in {time.time() - t_clean:.2f}s.")

    print("\n--- TRANSCRIPT ---")
    print(final_text)
    print("------------------")

    if copy_to_clipboard:
        import pyperclip
        pyperclip.copy(final_text)
        print("(Copied to clipboard)")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)
        print(f"(Saved to {output_path})")


def main():
    parser = argparse.ArgumentParser(description="VoiceBud: Fully offline speech dictation and audio file transcription.")
    parser.add_argument("-f", "--file", help="Path to an audio file to transcribe directly from CLI")
    parser.add_argument("-o", "--output", help="Save CLI transcription output to this text file")
    parser.add_argument("-c", "--clipboard", action="store_true", help="Copy transcription output to clipboard")
    parser.add_argument("--clean", action="store_true", help="Apply LLM cleanup in CLI mode")
    args = parser.parse_args()

    # If --file is provided, run in CLI batch mode and exit
    if args.file:
        run_cli_file_transcription(
            file_path=args.file,
            output_path=args.output,
            copy_to_clipboard=args.clipboard,
            run_clean=args.clean,
        )
        return

    # Normal background app mode
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    check_permissions()

    print(f"Loading STT model ({cfg['stt']['model']})...")
    stt = Transcriber(cfg["stt"])
    cleaner = Cleaner(cfg["llm"])
    rec = Recorder(
        sample_rate=cfg["audio"]["sample_rate"],
        channels=cfg["audio"]["channels"],
        preroll_ms=cfg["audio"]["preroll_ms"],
    )
    rec.start_stream()
    overlay = Overlay(lambda: rec.level)

    def on_press():
        rec.start()
        overlay.show()

    def process(audio):
        t0 = time.time()
        raw = stt.transcribe(audio)
        if not raw:
            print("(no speech detected)")
            return
        text = cleaner.clean(raw)
        inject.inject(text, cfg["inject"])
        print(f'→ "{text}"  ({time.time() - t0:.2f}s)')

    def on_release():
        audio = rec.stop()
        overlay.hide()
        threading.Thread(target=process, args=(audio,), daemon=True).start()

    key = cfg["hotkey"]["key"]
    mode = cfg["hotkey"].get("mode", "hold")
    PushToTalk(key, on_press, on_release, mode=mode).start()
    action = "Press" if mode == "toggle" else "Hold"
    print(f"{APP_NAME} ready. {action} [{key}] to dictate ({mode} mode).")

    def open_file_transcriber(*args):
        """Open the audio file transcription dialog."""
        if hasattr(overlay, "root"):
            def show_dialog():
                TranscribeWindow(overlay.root, stt, cleaner)
            overlay.root.after(0, show_dialog)

    if IS_MACOS:
        try:
            from AppKit import NSApplication, NSMenu, NSMenuItem, NSStatusBar
            from PyObjCTools import AppHelper

            rename_app()
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(1)  # accessory: no Dock icon

            status = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)
            status.button().setTitle_("🎙️")
            menu = NSMenu.alloc().init()
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"{APP_NAME} — press {key} to dictate", None, ""
            )
            item.setEnabled_(False)
            menu.addItem_(item)

            file_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Transcribe Audio File...", "openTranscribe:", "o"
            )
            menu.addItem_(file_item)

            quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Quit " + APP_NAME, "terminate:", "q"
            )
            menu.addItem_(quit_item)
            status.setMenu_(menu)

            try:
                AppHelper.runEventLoop()
            finally:
                rec.close()
            return
        except ImportError:
            pass

    # Windows / Linux main loop
    tray_icon = None

    def quit_app(*args):
        nonlocal tray_icon
        if tray_icon is not None:
            tray_icon.stop()
        try:
            rec.close()
        except Exception:
            pass
        overlay.close()
        sys.exit(0)

    tray_icon = create_windows_tray(key, open_file_transcriber, quit_app)
    if tray_icon is not None:
        tray_icon.run_detached()

    # Enable responsive Ctrl+C handling in Tkinter
    if hasattr(overlay, "root"):
        def poll_signals():
            overlay.root.after(200, poll_signals)

        overlay.root.after(200, poll_signals)
        signal.signal(signal.SIGINT, quit_app)

    try:
        overlay.mainloop()
    finally:
        try:
            rec.close()
        except Exception:
            pass
        if tray_icon is not None:
            tray_icon.stop()


if __name__ == "__main__":
    main()
