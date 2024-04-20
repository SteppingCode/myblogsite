# Используем официальный образ Python
FROM python:3.9-slim

COPY requirements.txt /app/requirements.txt

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY / /app

# Открытие порта 3000
EXPOSE 3000

# Запуск приложения
CMD ["python", "app.py"]
