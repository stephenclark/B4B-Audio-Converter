FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY split_audiobook.py /usr/local/bin/split_audiobook.py
RUN chmod +x /usr/local/bin/split_audiobook.py
CMD ["bash"]
