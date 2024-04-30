FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y git

COPY . .

ENV GIT_PYTHON_REFRESH quiet

EXPOSE 443

CMD ["gunicorn", "-b", "0.0.0.0:443", "app:app"]
