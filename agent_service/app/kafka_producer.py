from kafka import KafkaProducer, errors
import json
import os
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_OUT = os.getenv("TOPIC_OUT", "agent-tasks-completed")

def get_kafka_producer(retries=5, delay=2):
    for i in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda m: json.dumps(m).encode("utf-8")
            )
        except errors.NoBrokersAvailable:
            print(f"[Kafka] Broker unavailable. Retry {i+1}/{retries}...")
            time.sleep(delay)
    raise Exception("Kafka broker unavailable after retries")

def produce_result(result: dict):
    print("Producing result to Kafka:", result)
    producer = get_kafka_producer()
    producer.send(TOPIC_OUT, value=result)
    producer.flush()
