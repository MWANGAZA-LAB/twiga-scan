import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry():
    """Initialize Sentry SDK for error tracking"""
    sentry_dsn = os.getenv("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("VERSION", "1.0.0"),
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=0.1,
            # By setting the trace rate to 1.0, we capture 100% of transactions
            # for performance monitoring. We recommend adjusting this value in
            # production.
            profiles_sample_rate=0.1,
        )

        # Add custom tags
        sentry_sdk.set_tag("service", "twiga-scan-backend")
        sentry_sdk.set_tag("component", "api")

        return True
    return False
