FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY . .
RUN pip install -r requirements.txt

RUN pip install wait-for-it
CMD ["wait-for-it" , "--service", "rabbitmq:5672" , "--" , "python", "main.py"]