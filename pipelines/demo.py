# pylint: disable=no-value-for-parameter

import dagster as dg
from dagster_aws.s3 import s3_pickle_io_manager, s3_resource
from dagster_celery_docker.executor import celery_docker_executor


@dg.resource
def buggy_resource():
    # E.g. pyspark, opencv
    print("Hey, I'm going to ruin everything =)")
    return 42


@dg.solid(required_resource_keys={"buggy_resource"})
def hello(context):
    context.log.info("Hello, world!")
    context.log.info(context.resources.buggy_resource)


default_mode = dg.ModeDefinition(
    "default",
    executor_defs=dg.default_executors + [celery_docker_executor],
    resource_defs={
        "s3": s3_resource,
        "io_manager": s3_pickle_io_manager,
        "buggy_resource": buggy_resource,
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
                        "env_vars": [
                            "DAGSTER_POSTGRES_USER",
                            "DAGSTER_POSTGRES_PASSWORD",
                            "DAGSTER_POSTGRES_DB",
                            "AWS_ACCESS_KEY_ID",
                            "AWS_SECRET_ACCESS_KEY",
                        ],
                        "network": "dagster-celery-docker-bug_default",
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
