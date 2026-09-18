"""Local STT via faster-whisper (CTranslate2) with Silero VAD gating silence.
Supports both real-time numpy audio buffers and audio file paths (MP3, WAV, M4A, FLAC, etc.)."""
import os
import numpy as np


class Transcriber:
    def __init__(self, cfg):
        self.cfg = cfg
        engine = cfg.get("engine", "faster-whisper")
        if engine == "mlx-whisper":
            import mlx_whisper  # optional Neural-Engine path
            self._mlx = mlx_whisper
            self._model = None
        else:
            from faster_whisper import WhisperModel
            self._mlx = None
            self._model = WhisperModel(
                cfg.get("model", "base"),
                device="cpu",
                compute_type=cfg.get("compute_type", "int8"),
            )

    def transcribe(self, audio, progress_callback=None):
        """Transcribe audio.
        audio: either a mono float32 numpy array at 16kHz OR a path to an audio file (str/Path).
        progress_callback: optional callable(fraction: float, segment_text: str) for file transcription.
        Returns text.
        """
        is_file = isinstance(audio, (str, os.PathLike))

        if not is_file:
            if isinstance(audio, np.ndarray) and audio.size == 0:
                return ""

        if self._mlx is not None:
            result = self._mlx.transcribe(audio, language=self.cfg.get("language"))
            return result.get("text", "").strip()

        segments, info = self._model.transcribe(
            str(audio) if is_file else audio,
            language=self.cfg.get("language"),
            vad_filter=True,
            beam_size=1,
        )

        texts = []
        total_duration = getattr(info, "duration", 0.0) or 0.0

        for seg in segments:
            txt = seg.text.strip()
            if txt:
                texts.append(txt)
            if progress_callback is not None and total_duration > 0:
                progress_callback(min(1.0, seg.end / total_duration), txt)

        if progress_callback is not None:
            progress_callback(1.0, "")

        return " ".join(texts).strip()
