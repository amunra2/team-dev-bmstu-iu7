FROM python:3.11.3
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /bot

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY .env .
RUN export $(cat .env | xargs)
ENV DATA_URL="http://host.docker.internal:5050/"

COPY . .
CMD ["python3", "main.py"]
