import pika
import json

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'vote_queue'

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

# Ensure the message is a valid JSON string
message = json.dumps({"message": "Hello, RabbitMQ!"})

channel.basic_publish(exchange='',
                      routing_key=RABBITMQ_QUEUE,
                      body=message,
                      properties=pika.BasicProperties(delivery_mode=2))  # Make message persistent

print("Sent message:", message)

connection.close()
