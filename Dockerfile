FROM python:3.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    keras==2.3.1 \
    tensorflow==2.3.1 \
    transformers==4.28.1 \
    urllib3 \
    ufal.chu_liu_edmonds \
    ufal.udpipe==1.3.1.1

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

WORKDIR /app

COPY . /app/

EXPOSE 3000

# https://github.com/ufal/udpipe/blob/udpipe-2/models-2.17/models_list.sh
CMD ["python", "udpipe2_server.py", "3000", "ukr", "uk_all-ud-2.17-251125:uk_all-ud-2.17-251125:uk:ukr", "assets/models/uk_all-ud-2.17-251125.model", "uk_iu", "https://ufal.mff.cuni.cz/udpipe/2/models#universal_dependencies_217_models"]
