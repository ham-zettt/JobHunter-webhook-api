FROM mcr.microsoft.com/playwright/python:v1.64.1-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY . .
RUN chmod +x docker/entrypoint.sh && mkdir -p /app/data /app/data/debug /app/data/secrets \
    && chown -R pwuser:pwuser /app

USER pwuser

EXPOSE 8000

CMD ["bash", "docker/entrypoint.sh"]
