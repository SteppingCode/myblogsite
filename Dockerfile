FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y git

COPY . .

ENV GIT_PYTHON_REFRESH quiet

CMD ["gunicorn", "-b", "blog.evgeniu-s.ru", "app:app"]
