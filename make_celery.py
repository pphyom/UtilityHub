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
    backend = config.Config.CELERY_RESULT_BACKEND
    broker = config.Config.CELERY_BROKER_URL

    cel = Celery(
        app.import_name,
        backend=backend,
        broker=broker,
    )
    # Celery config
    cel.conf.update(
        result_backend=backend,
        broker_url=broker,
        broker_connection_retry_on_startup=True,
        imports=["tasks"],
    )

    return cel
