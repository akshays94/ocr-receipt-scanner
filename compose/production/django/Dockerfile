# FROM python:3.6-alpine 
FROM python:3.5

ENV PYTHONUNBUFFERED 1

# RUN apk update \
#   # psycopg2 dependencies
#   && apk add --virtual build-deps gcc python3-dev musl-dev \
#   && apk add postgresql-dev \
#   # Pillow dependencies
#   && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
#   # CFFI dependencies
#   && apk add libffi-dev py-cffi

RUN apt-get update
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xvf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN mv wkhtmltox/bin/wkhtmlto* /usr/bin/ 


# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

# RUN addgroup -S django \
#     && adduser -S -G django django

RUN groupadd -r django \
    && useradd -r -g django django

COPY . /app

RUN chown -v -R django:django /app

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
RUN chown django /start

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
