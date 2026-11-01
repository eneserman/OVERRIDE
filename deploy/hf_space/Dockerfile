FROM python:3.13-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH HF_HOME=/home/user/.cache/huggingface PYTHONUNBUFFERED=1
WORKDIR /home/user/app

RUN pip install --no-cache-dir --user torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
# the encoder architecture and tokenizer, fetched at build time so a cold start only loads the checkpoints
RUN python -c "from transformers import AutoModel, AutoTokenizer; AutoTokenizer.from_pretrained('microsoft/deberta-v3-base'); AutoModel.from_pretrained('microsoft/deberta-v3-base')"

COPY --chown=user . .
# the frozen seeds live in a model repo (a Space holds at most 1 GB); fetched at build time
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('enes123erman/override-checkpoints', local_dir='.', allow_patterns=['checkpoints/*'])"
ENV OVERRIDE_CORS_ORIGINS=https://override-demo.vercel.app
EXPOSE 7860
CMD ["python", "app/server.py", "--checkpoints-no", "checkpoints/no/*.pt", "--checkpoints-history", "checkpoints/tail60/*.pt", "--host", "0.0.0.0", "--port", "7860"]
