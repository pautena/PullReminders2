import sentry_sdk
import settings
from sentry_sdk.integrations.aws_lambda import \
    AwsLambdaIntegration


def _get_integrations():
    return [AwsLambdaIntegration()]


def initialize(dsn=settings.SENTRY_DSN):
    sentry_sdk.init(
        dsn,
        integrations=_get_integrations()
    )
