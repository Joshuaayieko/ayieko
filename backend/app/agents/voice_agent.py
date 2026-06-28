"""Voice agent — speech-to-text and text-to-speech hooks.

The actual STT/TTS engines (Whisper, Piper/Coqui) are heavy native dependencies,
so this module defines the integration surface and provides clear stubs. Wire in
the real engines where indicated, or run STT/TTS on-device in the Flutter app.
"""

from __future__ import annotations

WAKE_WORD = "hey orbes"


class VoiceAgent:
    """Surface for the voice pipeline: STT -> planner -> TTS."""

    def detect_wake_word(self, transcript: str) -> bool:
        return WAKE_WORD in transcript.lower()

    def transcribe(self, audio_bytes: bytes) -> str:
        """Speech-to-text. Plug in Whisper here.

        Example (faster-whisper):
            from faster_whisper import WhisperModel
            model = WhisperModel("base")
            segments, _ = model.transcribe(audio_path)
            return " ".join(s.text for s in segments)
        """
        raise NotImplementedError(
            "Wire in a Whisper model (e.g. faster-whisper) to enable transcription."
        )

    def synthesize(self, text: str) -> bytes:
        """Text-to-speech. Plug in Piper or Coqui TTS here and return audio bytes."""
        raise NotImplementedError(
            "Wire in Piper or Coqui TTS to enable speech synthesis."
        )
