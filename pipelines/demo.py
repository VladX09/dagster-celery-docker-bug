# pylint: disable=no-value-for-parameter

import dagster as dg
from dagster_aws.s3 import s3_pickle_io_manager, s3_resource
from dagster_celery_docker.executor import celery_docker_executor


@dg.solid
def hello(context):
    context.log.info("Hello, world!")


default_mode = dg.ModeDefinition(
    "default",
    executor_defs=dg.default_executors + [celery_docker_executor],
    resource_defs={
        "s3": s3_resource,
        "io_manager": s3_pickle_io_manager,
    },
)
default_preset = dg.PresetDefinition(
    "default",
    mode="default",
    run_config={
        "resources": {
            "s3": {
                "config": {
                    "endpoint_url": "http://minio:9000",
                },
            },
            "io_manager": {
                "config": {
                    "s3_bucket": "demo",
                    "s3_prefix": "demo",
                },
            },
        },
        "execution": {
            "celery-docker": {
                "config": {
                    "docker": {
                        "image": "pipelines-image",
                    },
                    "broker": "pyamqp://rabbitmq:rabbitmq@rabbitmq:5672/dagster",
                },
            },
        },
    },
)


@dg.pipeline(mode_defs=[default_mode], preset_defs=[default_preset])
def demo_pipeline():
    hello()
