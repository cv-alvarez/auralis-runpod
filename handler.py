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
    print(f"Cargando modelos: {TTS_MODEL_ID}, {GPT_MODEL_ID}")
    tts = TTS().from_pretrained(TTS_MODEL_ID, gpt_model=GPT_MODEL_ID)
    print("✅ Modelos cargados exitosamente")
except Exception as e:
    raise RuntimeError(f"Error cargando modelo TTS ({TTS_MODEL_ID}, {GPT_MODEL_ID}): {e}")

def _safe_format(fmt: str) -> str:
    if not fmt:
        return "wav"
    fmt = fmt.lower().strip()
    return fmt if fmt in ("mp3", "wav") else "wav"

def generate(job):
    """
    Input esperado:
    {
      "text": "Hola esto es una prueba.",
      "language": "es",
      "format": "wav",
      "speaker_files": ["https://..."] # OPCIONAL - si no se provee, usa voz predeterminada
    }
    """
    try:
        ip = (job or {}).get("input", {}) or {}

        text = (ip.get("text") or "").strip()
        if not text:
            return {"error": "text requerido"}

        language = (ip.get("language") or "es").strip()
        fmt = _safe_format(ip.get("format", "wav"))
        # ❌ REMOVIDO: speed = float(ip.get("speed", 1.0))  # No existe en Auralis

        speaker_files = ip.get("speaker_files")
        
        # ✅ CORREGIDO: Manejo opcional de speaker_files
        if speaker_files is not None and not isinstance(speaker_files, (list, tuple)):
            return {"error": "speaker_files debe ser lista de URLs o null"}

        # ✅ CORREGIDO: Crear request sin parámetro speed
        if speaker_files:
            # Con clonación de voz
            req = TTSRequest(
                text=text,
                language=language,
                speaker_files=speaker_files,
            )
        else:
            # Sin clonación - voz predeterminada
            req = TTSRequest(
                text=text,
                language=language,
            )

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, f"out.{fmt}")
            
            print(f"Generando audio: {len(text)} chars, formato: {fmt}")
            audio = tts.generate_speech(req)
            audio.save(out_path)

            with open(out_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

        mime = "audio/wav" if fmt == "wav" else "audio/mpeg"
        return {
            "success": True,  # ✅ CAMBIADO de "ok" a "success"
            "format": fmt,
            "mime": mime,
            "audio_base64": b64
        }

    except Exception as e:
        error_msg = str(e)
        trace = traceback.format_exc()
        print(f"❌ Error: {error_msg}")
        print(trace)
        
        return {
            "success": False,
            "error": error_msg,
            "trace": trace[:2000]
        }

# Inicia el serverless handler
if __name__ == "__main__":
    runpod.serverless.start({"handler": generate})