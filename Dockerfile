FROM python:3.11.3-slim AS BMSTUFindEmptyAudienceBot

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN mkdir -p /bot
ADD . /bot
WORKDIR /bot

RUN pip3 install -r requirements.txt
CMD python3 /bot/main.py
