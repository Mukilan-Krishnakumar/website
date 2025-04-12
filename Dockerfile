FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /website

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

#ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE=website.settings
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y gcc python3-dev libpq-dev gunicorn
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*


RUN mkdir -p /website
RUN mkdir -p /website/static
RUN mkdir -p /website/media


#COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Place executables in the environment at the front of the path
ENV PATH="/website/.venv/bin:$PATH"
ENTRYPOINT []

RUN useradd -m appuser && chown -R appuser:appuser /website
USER appuser
WORKDIR /website
COPY . /website
RUN uv sync --frozen

EXPOSE 8000
CMD ["bash", "start.sh"]