FROM python:3.10

WORKDIR /app

EXPOSE 8080/tcp

COPY . .

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.app.run:app
