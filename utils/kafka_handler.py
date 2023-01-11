from kafka import KafkaProducer


class KafkaHandler:
    def __init__(self, kafka_bootstrap: str, topic: str):
        self.kafka_bootstrap = kafka_bootstrap
        self.topic = topic

    def send_message_to_topic(self, message: str):
        self.producer = KafkaProducer(
            bootstrap_servers=[self.kafka_bootstrap], value_serializer=lambda x: x.encode("utf-8")
        )
        self.producer.send(self.topic, value=message)
        self.producer.flush()
        self.producer.close()
