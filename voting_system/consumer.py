# consumer.py
import pika
import json

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Received vote: {message}")
    except Exception as e:
        print(f"Error processing message: {e}")

def start_consumer():
    try:
        # Establish a connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue (ensure it matches the queue name in your Django view)
        channel.queue_declare(queue='vote_queue', durable=True)

        # Set up the consumer
        channel.basic_consume(queue='vote_queue', on_message_callback=callback, auto_ack=True)

        print("🎧 Waiting for vote messages...")
        channel.start_consuming()  # Start listening for messages
    except Exception as e:
        print(f"Failed to start consumer: {e}")

if __name__ == "__main__":
    start_consumer()