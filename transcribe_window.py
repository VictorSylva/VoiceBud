"""VoiceBud - Audio File Transcription Window.
Provides a modern dark-themed GUI for selecting, transcribing, previewing,
editing, LLM-cleaning, copying, and saving audio file transcripts.
"""
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pyperclip

AUDIO_FILETYPES = [
    ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.opus"),
    ("MP3 Audio", "*.mp3"),
    ("WAV Audio", "*.wav"),
    ("M4A Audio", "*.m4a"),
    ("FLAC Audio", "*.flac"),
    ("All Files", "*.*"),
]


class TranscribeWindow:
    def __init__(self, master, stt, cleaner=None, initial_file=None):
        self.master = master
        self.stt = stt
        self.cleaner = cleaner

        self.current_file = None
        self.raw_text = ""
        self.cleaned_text = ""
        self.showing_cleaned = False
        self._is_processing = False

        # Create window
        self.win = tk.Toplevel(master) if master else tk.Tk()
        self.win.title("VoiceBud — Transcribe Audio File")
        self.win.geometry("740x580")
        self.win.minsize(580, 440)
        self.win.configure(bg="#121214")

        # Bring window to front
        self.win.lift()
        self.win.attributes("-topmost", True)
        self.win.after(150, lambda: self.win.attributes("-topmost", False))

        self._build_ui()

        if initial_file:
            self.load_and_transcribe(initial_file)

    def _build_ui(self):
        # Top Header Card
        header_frame = tk.Frame(self.win, bg="#18181b", padx=16, pady=12)
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        title_label = tk.Label(
            header_frame,
            text="🎙️ Audio File Transcription",
            font=("Segoe UI", 13, "bold"),
            fg="#f4f4f5",
            bg="#18181b",
        )
        title_label.pack(anchor="w")

        file_row = tk.Frame(header_frame, bg="#18181b")
        file_row.pack(fill="x", pady=(8, 0))

        self.file_label = tk.Label(
            file_row,
            text="No audio file selected",
            font=("Segoe UI", 9),
            fg="#a1a1aa",
            bg="#18181b",
            anchor="w",
        )
        self.file_label.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            file_row,
            text="Choose Audio File...",
            font=("Segoe UI", 9, "bold"),
            bg="#8b5cf6",
            fg="#ffffff",
            activebackground="#a78bfa",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._on_browse,
        )
        browse_btn.pack(side="right")

        # Progress & Status Bar
        status_frame = tk.Frame(self.win, bg="#121214", padx=16)
        status_frame.pack(fill="x", pady=(4, 6))

        self.status_label = tk.Label(
            status_frame,
            text="Ready. Select an audio file to transcribe.",
            font=("Segoe UI", 9),
            fg="#a1a1aa",
            bg="#121214",
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self.view_badge = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 8, "bold"),
            fg="#a36bff",
            bg="#18181b",
            padx=6,
            pady=1,
        )
        self.view_badge.pack(side="right")

        # Progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "VoiceBud.Horizontal.TProgressbar",
            troughcolor="#18181b",
            background="#8b5cf6",
            thickness=6,
        )
        self.progress_bar = ttk.Progressbar(
            self.win,
            style="VoiceBud.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 8))

        # Text Area Card
        text_card = tk.Frame(self.win, bg="#18181b", padx=10, pady=10)
        text_card.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.text_box = tk.Text(
            text_card,
            wrap="word",
            font=("Segoe UI", 10),
            bg="#27272a",
            fg="#f4f4f5",
            insertbackground="#f4f4f5",
            selectbackground="#8b5cf6",
            selectforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=10,
            undo=True,
        )
        scrollbar = ttk.Scrollbar(text_card, orient="vertical", command=self.text_box.yview)
        self.text_box.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.text_box.pack(side="left", fill="both", expand=True)

        # Bottom Action Bar
        action_frame = tk.Frame(self.win, bg="#121214", padx=16, pady=8)
        action_frame.pack(fill="x", side="bottom")

        # Action buttons on left
        self.copy_btn = tk.Button(
            action_frame,
            text="📋 Copy to Clipboard",
            font=("Segoe UI", 9, "bold"),
            bg="#27272a",
            fg="#f4f4f5",
            activebackground="#3f3f46",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            state="disabled",
            command=self._on_copy,
        )
        self.copy_btn.pack(side="left", padx=(0, 8))

        self.save_btn = tk.Button(
            action_frame,
            text="💾 Save as .txt...",
            font=("Segoe UI", 9),
            bg="#27272a",
            fg="#f4f4f5",
            activebackground="#3f3f46",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            state="disabled",
            command=self._on_save,
        )
        self.save_btn.pack(side="left", padx=(0, 8))

        # LLM toggle button
        self.clean_btn = tk.Button(
            action_frame,
            text="✨ Clean with LLM",
            font=("Segoe UI", 9),
            bg="#3b1f66",
            fg="#e9d5ff",
            activebackground="#581c87",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            state="disabled",
            command=self._on_toggle_cleanup,
        )
        self.clean_btn.pack(side="left")

        # Close button on right
        close_btn = tk.Button(
            action_frame,
            text="Close",
            font=("Segoe UI", 9),
            bg="#27272a",
            fg="#a1a1aa",
            activebackground="#3f3f46",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.win.destroy,
        )
        close_btn.pack(side="right")

    def _on_browse(self):
        if self._is_processing:
            return
        file_path = filedialog.askopenfilename(
            parent=self.win,
            title="Select Audio File to Transcribe",
            filetypes=AUDIO_FILETYPES,
        )
        if file_path:
            self.load_and_transcribe(file_path)

    def load_and_transcribe(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"Could not find audio file:\n{file_path}", parent=self.win)
            return

        self.current_file = file_path
        filename = os.path.basename(file_path)
        filesize_mb = os.path.getsize(file_path) / (1024 * 1024)
        self.file_label.config(text=f"{filename} ({filesize_mb:.1f} MB)")

        self.raw_text = ""
        self.cleaned_text = ""
        self.showing_cleaned = False
        self.view_badge.config(text="")
        self._set_text("")
        self._set_buttons_state("disabled")

        self._is_processing = True
        self.progress_bar["value"] = 0
        self.status_label.config(text="Transcribing audio with Whisper...", fg="#a36bff")

        def run():
            t0 = time.time()
            try:
                def on_progress(frac, seg_text):
                    self.win.after(0, lambda f=frac: self._update_progress(f))

                text = self.stt.transcribe(file_path, progress_callback=on_progress)
                elapsed = time.time() - t0
                self.win.after(0, lambda: self._on_transcribe_done(text, elapsed))
            except Exception as e:
                self.win.after(0, lambda err=e: self._on_transcribe_error(str(err)))

        threading.Thread(target=run, daemon=True).start()

    def _update_progress(self, fraction):
        val = int(fraction * 100)
        self.progress_bar["value"] = val
        self.status_label.config(text=f"Transcribing audio... ({val}%)")

    def _on_transcribe_done(self, text, elapsed):
        self._is_processing = False
        self.progress_bar["value"] = 100
        self.raw_text = text
        self.showing_cleaned = False

        if not text:
            self.status_label.config(text=f"Completed in {elapsed:.1f}s (no speech detected).", fg="#e4e4e7")
            self._set_text("(No speech detected in audio file)")
            self._set_buttons_state("disabled")
            return

        word_count = len(text.split())
        self.status_label.config(
            text=f"Transcribed in {elapsed:.1f}s ({word_count} words).",
            fg="#4ade80",
        )
        self.view_badge.config(text="RAW WHISPER")
        self._set_text(text)
        self._set_buttons_state("normal")
        self.clean_btn.config(text="✨ Clean with LLM")

    def _on_transcribe_error(self, err_msg):
        self._is_processing = False
        self.progress_bar["value"] = 0
        self.status_label.config(text=f"Error: {err_msg}", fg="#f87171")
        messagebox.showerror("Transcription Error", f"Failed to transcribe audio:\n{err_msg}", parent=self.win)

    def _on_toggle_cleanup(self):
        if self._is_processing or not self.raw_text:
            return

        # If already cleaned and currently showing cleaned, switch back to raw
        if self.showing_cleaned:
            self.showing_cleaned = False
            self._set_text(self.raw_text)
            self.clean_btn.config(text="✨ Show Cleaned")
            self.view_badge.config(text="RAW WHISPER")
            return

        # If already cleaned and currently showing raw, switch to cleaned
        if self.cleaned_text:
            self.showing_cleaned = True
            self._set_text(self.cleaned_text)
            self.clean_btn.config(text="↺ Show Raw")
            self.view_badge.config(text="CLEANED (LLM)")
            return

        # Not yet cleaned: call LLM cleaner
        if not self.cleaner or not getattr(self.cleaner, "enabled", False):
            # Check if cleaner can be reached
            if self.cleaner and not self.cleaner._model_available():
                messagebox.showwarning(
                    "Ollama Not Running",
                    f"Ollama is not running or model '{self.cleaner.model}' is not pulled.\n\n"
                    f"Run: ollama serve\nAnd: ollama pull {self.cleaner.model}",
                    parent=self.win,
                )
                return

        self._is_processing = True
        self.status_label.config(text="Cleaning transcript with local LLM (Ollama)...", fg="#a36bff")
        self.clean_btn.config(state="disabled")

        def run_clean():
            t0 = time.time()
            try:
                cleaned = self.cleaner.clean(self.raw_text) if self.cleaner else self.raw_text
                elapsed = time.time() - t0
                self.win.after(0, lambda: self._on_clean_done(cleaned, elapsed))
            except Exception as e:
                self.win.after(0, lambda err=e: self._on_clean_error(str(err)))

        threading.Thread(target=run_clean, daemon=True).start()

    def _on_clean_done(self, cleaned, elapsed):
        self._is_processing = False
        self.cleaned_text = cleaned
        self.showing_cleaned = True
        self._set_text(cleaned)
        self.status_label.config(text=f"Cleaned via Ollama in {elapsed:.1f}s.", fg="#4ade80")
        self.clean_btn.config(text="↺ Show Raw", state="normal")
        self.view_badge.config(text="CLEANED (LLM)")

    def _on_clean_error(self, err_msg):
        self._is_processing = False
        self.status_label.config(text=f"Cleanup error ({err_msg}); using raw transcript.", fg="#f87171")
        self.clean_btn.config(state="normal")

    def _on_copy(self):
        content = self.text_box.get("1.0", "end-1c").strip()
        if not content:
            return
        pyperclip.copy(content)
        orig_text = self.copy_btn.cget("text")
        self.copy_btn.config(text="✓ Copied!", bg="#15803d", fg="#ffffff")
        self.win.after(1500, lambda: self.copy_btn.config(text=orig_text, bg="#27272a", fg="#f4f4f5"))

    def _on_save(self):
        content = self.text_box.get("1.0", "end-1c").strip()
        if not content:
            return
        default_name = "transcript.txt"
        if self.current_file:
            base = os.path.splitext(os.path.basename(self.current_file))[0]
            default_name = f"{base}_transcript.txt"

        save_path = filedialog.asksaveasfilename(
            parent=self.win,
            title="Save Transcript",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_label.config(text=f"Saved transcript to {os.path.basename(save_path)}.", fg="#4ade80")

    def _set_text(self, text):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", text)

    def _set_buttons_state(self, state):
        self.copy_btn.config(state=state)
        self.save_btn.config(state=state)
        self.clean_btn.config(state=state)
