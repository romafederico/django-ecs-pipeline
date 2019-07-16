FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV BUKIUM_ENV=develop
COPY requirements /config/
RUN pip install -r /config/requirements
WORKDIR /opt/bukium-api
COPY bin/ bin/
COPY src/ src/
CMD ["bin/start_django.sh"]