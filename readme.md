# Auralis TTS on RunPod (Serverless)

## Deploy
1) Sube este repo a tu GitHub.
2) En RunPod → **Deploy a New Serverless Endpoint** → **Connect GitHub** → elige este repo.
3) Elige **CPU** para prueba o **GPU (A10/A100)** para producción/voz clonada.
4) (Opcional) Env vars:
   - `AURALIS_TTS_MODEL=AstraMindAI/xttsv2`
   - `AURALIS_GPT_MODEL=AstraMindAI/xtts2-gpt`
5) Deploy. Espera a que el endpoint esté **Ready**.

## Probar en la pestaña *Requests*
```json
{
  "input": {
    "text": "Hola, esto es Auralis leyendo un resumen en español.",
    "language": "es",
    "format": "mp3",
    "speed": 1.0
  }
}
