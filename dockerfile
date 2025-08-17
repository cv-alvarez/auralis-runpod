
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# Instalar PyTorch primero
RUN pip install torch==2.3.1+cu121 torchaudio==2.3.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Instalar dependencias específicas una por una
RUN pip install runpod==1.6.2
RUN pip install auralis
RUN pip install soundfile==0.12.1
RUN pip install numpy==1.24.4

WORKDIR /app

# Copiar solo el handler (sin requirements.txt)
COPY handler.py .

CMD ["python3", "handler.py"]