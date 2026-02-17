import connexion
from connexion import NoContent
import uuid
import datetime
import yaml
import json
import logging.config
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("conf_log.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

# Initialize Kafka Client
# Accessing config values: e.g., app_config['events']['hostname']
kafka_server = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
client = KafkaClient(hosts=kafka_server)
topic = client.topics[str.encode(app_config['events']['topic'])]
producer = topic.get_sync_producer()

def process_meal_batch(body):
    """ Process a batch of meal events and push to Kafka """
    process_events(body, "meal")
    return NoContent, 201

def process_exercise_batch(body):
    """ Process a batch of exercise events and push to Kafka """
    process_events(body, "exercise")
    return NoContent, 201

def process_events(body, event_type):
    """ Helper to format and produce messages to Kafka """
    user_id = body.get("user_id")
    device = body.get("source_device")
    batch_ts = body.get("timestamp")
    items = body.get("items", [])

    for item in items:
        # 1. Prepare the payload
        trace_id = str(uuid.uuid4())
        item['user_id'] = user_id
        item['trace_id'] = trace_id
        item['source_device'] = device
        item['batch_timestamp'] = batch_ts
        item['record_timestamp'] = item.pop('timestamp', None)

        # 2. Construct the Kafka message wrapper
        msg = {
            "type": event_type,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "payload": item
        }

        # 3. Produce to Kafka
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        
        logger.info(f"Produced {event_type} event with trace_id: {trace_id}")

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)