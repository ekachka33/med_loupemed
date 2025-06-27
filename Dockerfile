# Используем официальный образ Python как базовый
FROM python:3.10-slim-buster

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости перед копированием всего проекта
# Это позволяет Docker кэшировать слои и ускорять пересборку
COPY requirements.txt /app/

# Устанавливаем системные зависимости, необходимые для psycopg2 и других библиотек
RUN apt-get update && apt-get install -y     gcc     postgresql-client     libpq-dev     netcat     && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальную часть кода приложения
COPY . /app/

# Открываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения (пока оставим её простой, потом настроим)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
