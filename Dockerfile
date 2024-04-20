# Используем официальный образ Python
FROM python:3.9-slim

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY .github/workflows /app

# Открытие порта 5000
EXPOSE 3000

# Запуск приложения
CMD ["python", "app.py"]
