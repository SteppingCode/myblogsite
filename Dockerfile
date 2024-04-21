# Используем официальный образ Python
FROM python:3.9-slim

# Копируем файл requirements.txt в контейнер
COPY requirements.txt /app/requirements.txt

# Установка зависимостей
RUN pip install --no-cache-dir -r /app/requirements.txt

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app

# Открытие порта 443
EXPOSE 443

# Запуск приложения
CMD ["python", "app.py"]
