FROM python:3.8-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY ["init_db.py", "schema.sql", "."]
RUN python init_db.py
COPY /techtrends/requirements.txt .
RUN python -m pip install -r requirements.txt
WORKDIR /app
COPY . /app
RUN adduser -u 4444 --disabled-password --gecos "" appuser && chown -R appuser /app
EXPOSE 3111
USER appuser
CMD ["python", "app.py"]