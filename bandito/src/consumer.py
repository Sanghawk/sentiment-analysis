import pika

# Connect to RabbitMQ in Docker
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

# Ensure queue exists
channel.queue_declare(queue="sitemap_links")

def callback(ch, method, properties, body):
    print(f" [x] Processed {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge completion

channel.basic_consume(queue="sitemap_links", on_message_callback=callback)

print(" [*] Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()