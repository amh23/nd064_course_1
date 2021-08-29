FROM python:2.7
LABEL maintainer="amh"

COPY . /techtrends
WORKDIR /techtrends

EXPOSE 3111
RUN pip install -r requirements.txt && \
    python init_db.py

# command to run on container start
CMD ["python", "app.py"]
