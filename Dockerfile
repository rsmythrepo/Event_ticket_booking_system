FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=app.py
ENV ENCRYPTION_KEY="$(cat /app/secrets/encryption_key)"

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]


