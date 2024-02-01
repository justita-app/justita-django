# This docker file is used for production
# Creating image based on official python3 image
FROM python:3.11

# Installing all python dependencies
ADD requirements/ requirements/
COPY requirements.txt .

# Install system dependencies required for building twisted-iocpsupport
RUN apt-get update && \
    apt-get install -y build-essential python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python -m pip install -r requirements.txt && \
    pip install ipython==8.2.0 && \
    pip install gunicorn==20.1.0 && \
    pip install twisted==22.4.0

ENV HOME=/app
ENV APP_HOME=/app/justita_django_app
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app && \
    groupadd -r appuser && useradd --no-log-init -r -g appuser appuser && \
    python -m pip install --upgrade pip && \
    mkdir ${APP_HOME} ${APP_HOME}/logs

WORKDIR ${APP_HOME}
EXPOSE 8000

# Copy application code
COPY . ${APP_HOME}
