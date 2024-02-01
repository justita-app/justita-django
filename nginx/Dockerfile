FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
ADD default.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /app/justita_django_app/static && \
    mkdir -p /app/justita_django_app/media && \
    chmod 755 /app/justita_django_app/static && \
    chmod 755 /app/justita_django_app/media

VOLUME /app/justita_django_app/static
VOLUME /app/justita_django_app/media