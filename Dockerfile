FROM python:3.10

WORKDIR /app

EXPOSE 8080/tcp

COPY . .

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD ["gunicorn", "--timeout", "0", "-w", "4", "src.server.server_main:app"]
