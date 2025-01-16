import config
from celery import Celery


def make_celery(app):
    """
    Create a new Celery object and tie the Celery config to the Flask app's config.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        Celery: A configured Celery object.
    """
    cel = Celery(
        app.import_name,
        backend=config.Config.CELERY_RESULT_BACKEND,
        broker=config.Config.CELERY_BROKER_URL,
    )
    # Celery config
    cel.conf.update(
        result_backend=config.Config.CELERY_RESULT_BACKEND,
        broker_url=config.Config.CELERY_BROKER_URL,
        broker_connection_retry_on_startup=True,
    )

    return cel
