FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# Instala torch con CUDA 12.1 (ajusta versión si lo necesitas)
RUN pip install torch==2.3.1+cu121 --index-url https://download.pytorch.org/whl/cu121

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY handler.py .

CMD ["python3", "handler.py"]
