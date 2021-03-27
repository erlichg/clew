FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN apk add --update py-pip
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev python3-dev openssl-dev cargo
COPY . .
RUN pip install -r requirements.txt
EXPOSE 4567

RUN pip install wait-for-it
CMD ["wait-for-it" , "--service", "rabbitmq:5672", "--service", "db:3306" , "--" , "python", "main.py"]