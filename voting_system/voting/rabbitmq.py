import pika
from django.conf import settings

def get_rabbitmq_connection():
    """Create and return a RabbitMQ connection and channel."""
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Ensure the queue exists and is durable
    channel.queue_declare(queue='vote_queue', durable=True)

    return connection, channel
