# Базовий образ з Python
FROM python:3.12-slim

# Не буферизувати вивід (щоб логі одразу були видні)
ENV PYTHONUNBUFFERED=1

# Робоча директорія всередині контейнера
WORKDIR /app

# Копіюємо файл з залежностями у контейнер
COPY requirements.txt /app/

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Тепер копіюємо весь проєкт у контейнер
COPY . /app/

# (Документаційно) відкриваємо порти HTTP та socket-сервера
EXPOSE 3000
EXPOSE 5000

# Команда для запуску додатку
CMD ["python", "main.py"]
