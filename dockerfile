FROM nvidia/cuda:12.4.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg libsndfile1 git \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# ❌ No instales torch manualmente (evita cu121)
# ✅ Instala dependencias en el orden correcto y mínimas necesarias
RUN pip install runpod==1.6.2
# auralis trae vLLM/torch compatibles con cu12.4
RUN pip install auralis
# utilidades de audio seguras
RUN pip install soundfile==0.13.1
# deja que auralis decida numpy; si igual quieres fijar:
# RUN pip install 'numpy>=1.26,<3'

WORKDIR /app
COPY handler.py .

CMD ["python3", "handler.py"]
