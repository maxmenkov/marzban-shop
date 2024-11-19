FROM python:3.10-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN ["pip", "install", "-r", "requirements.txt"]
COPY bot /app
ENTRYPOINT ["bash", "-c", "pybabel compile -d locales -D bot; alembic upgrade head; python main.py"]
