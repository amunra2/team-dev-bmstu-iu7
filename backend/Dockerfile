FROM python:3.11.3
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /bot-backend

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY .env .
RUN export $(cat .env | xargs)
ENV POSTGRES_HOST="host.docker.internal"

WORKDIR /bot-backend/backend
COPY backend .

RUN ["python3", "-m", "flask", "db", "upgrade"]
CMD ["python3", "-m", "flask", "--debug", "run", "--host=0.0.0.0", "--port=5050"]
