# handler.py — RunPod Serverless para TTS con Auralis
import os
import base64
import tempfile
import traceback

import runpod
from auralis import TTS, TTSRequest

# Modelos por defecto (puedes sobreescribir con env vars en RunPod)
TTS_MODEL_ID = os.getenv("AURALIS_TTS_MODEL", "AstraMindAI/xttsv2")
GPT_MODEL_ID = os.getenv("AURALIS_GPT_MODEL", "AstraMindAI/xtts2-gpt")

# Carga única por pod (warm start)
try:
    tts = TTS().from_pretrained(TTS_MODEL_ID, gpt_model=GPT_MODEL_ID)
except Exception as e:
    # Si falla aquí, verás el error en los logs del worker
    raise RuntimeError(f"Error cargando modelo TTS ({TTS_MODEL_ID}, {GPT_MODEL_ID}): {e}")

def _safe_format(fmt: str) -> str:
    if not fmt:
        return "mp3"
    fmt = fmt.lower().strip()
    return fmt if fmt in ("mp3", "wav") else "mp3"

def generate(job):
    """
    Input esperado:
    {
      "text": "Hola esto es una prueba.",
      "language": "es",                 # opcional (default: "es")
      "format": "mp3",                  # "mp3" | "wav" (default: "mp3")
      "speed": 1.0,                     # opcional
      "speaker_files": ["https://..."]  # opcional (1-3 muestras para clonación)
    }
    """
    try:
        ip = (job or {}).get("input", {}) or {}

        text = (ip.get("text") or "").strip()
        if not text:
            return {"error": "text requerido"}

        language = (ip.get("language") or "es").strip()
        fmt = _safe_format(ip.get("format", "mp3"))
        speed = float(ip.get("speed", 1.0))

        speaker_files = ip.get("speaker_files")
        if speaker_files is not None and not isinstance(speaker_files, (list, tuple)):
            return {"error": "speaker_files debe ser una lista de URLs o null"}

        req = TTSRequest(
            text=text,
            language=language,
            speaker_files=speaker_files,
            speed=speed,
        )

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, f"out.{fmt}")
            audio = tts.generate_speech(req)  # Auralis se encarga del chunking/streaming interno
            audio.save(out_path)

            with open(out_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

        mime = "audio/wav" if fmt == "wav" else "audio/mpeg"
        return {
            "ok": True,
            "format": fmt,
            "mime": mime,
            "audio_base64": b64
            # Si prefieres URL en vez de base64,
            # aquí puedes subir a tu storage (Firebase/S3) y devolver {"audio_url": "..."}
        }

    except Exception as e:
        # Devuelve el error al cliente y deja traza en logs para depurar
        return {
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc()[:4000]  # evita respuestas gigantes
        }

# Inicia el servidor serverless
runpod.serverless.start({"handler": generate})
