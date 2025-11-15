FROM python:3.14-slim
LABEL authors="Artem Tolokonnikov"

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \

  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=2.1.3

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libcap-dev \
    libpcre3-dev \
    libpq-dev \
    python3-distutils \
    uuid-dev \
    curl \
    bash \
    git \
    nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /var/ScheduleBotAiogram/
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root
COPY . /var/ScheduleBotAiogram
CMD ["python", ".\main.py"]
