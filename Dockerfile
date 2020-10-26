FROM python:3.9-slim-buster
LABEL maintainer="bomzheg <bomzheg@gmail.com>" \
      description="World lucky bets Telegram Bot"
COPY requirements.txt requirements.txt
RUN apt update -y \
    && apt install -y gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt purge -y gcc \
    && apt autoclean -y \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 3000
COPY app app
ENTRYPOINT ["python3", "-m", "app", "-p"]