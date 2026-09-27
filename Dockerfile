FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY frontend ./frontend
COPY migrations ./migrations
COPY alembic.ini ./
COPY scripts ./scripts
RUN pip install --no-cache-dir .
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["sh", "scripts/start.sh"]
