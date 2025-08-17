# handler.py — RunPod Serverless para TTS con Auralis
import os, base64, tempfile
import runpod
from auralis import TTS, TTSRequest

# Modelos por defecto (puedes cambiarlos con env vars del endpoint)
TTS_MODEL_ID = os.getenv("AURALIS_TTS_MODEL", "AstraMindAI/xttsv2")
GPT_MODEL_ID = os.getenv("AURALIS_GPT_MODEL", "AstraMindAI/xtts2-gpt")

# Se carga una sola vez por pod (warm)
tts = TTS().from_pretrained(TTS_MODEL_ID, gpt_model=GPT_MODEL_ID)

def generate(job):
    """
    INPUT esperado (ejemplo):
    {
      "text": "Hola esto es una prueba.",
      "language": "es",           // opcional (por defecto "es")
      "format": "mp3",            // "mp3" | "wav" (por defecto "mp3")
      "speed": 1.0,               // opcional
      "speaker_files": ["https://.../voz-ref.wav"]  // opcional
    }
    """
    ip = job.get("input", {}) or {}
    text = (ip.get("text") or "").strip()
    if not text:
        return {"error": "text requerido"}

    language = ip.get("language", "es")
    fmt = ip.get("format", "mp3").lower()
    speed = float(ip.get("speed", 1.0))
    speaker_files = ip.get("speaker_files")  # lista de URLs opcional

    req = TTSRequest(
        text=text,
        language=language,
        speaker_files=speaker_files,
        speed=speed,
    )

    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, f"out.{fmt if fmt in ('mp3','wav') else 'mp3'}")
        audio = tts.generate_speech(req)
        audio.save(out_path)

        with open(out_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

    mime = "audio/wav" if fmt == "wav" else "audio/mpeg"
    return {"format": fmt, "mime": mime, "audio_base64": b64}

# Inicia el servidor serverless
runpod.serverless.start({"handler": generate})
