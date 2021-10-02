FROM python:3.8-slim

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p ${DAGSTER_HOME}

COPY requirements.txt ${DAGSTER_HOME}
RUN pip install -r ${DAGSTER_HOME}/requirements.txt

COPY dagster.yaml workspace.yaml ${DAGSTER_HOME}
COPY pipelines /pipelines

WORKDIR ${DAGSTER_HOME}

