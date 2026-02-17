import logging.config
import yaml
import connexion
import functools
import json
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from connexion import NoContent
from models import Base, Meal, Exercise
import os
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

# --- 1. Configuration & Logging ---
base_dir = os.path.dirname(os.path.abspath(__file__))
app_config_path = os.path.join(base_dir, 'app_conf.yaml')
log_config_path = os.path.join(base_dir, 'log_conf.yml')

with open(app_config_path, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_config_path, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

# --- 2. Database Setup ---
datastore = app_config['datastore']
DB_URL = f"mysql+mysqldb://{datastore['user']}:{datastore['password']}@{datastore['hostname']}:{datastore['port']}/{datastore['db']}"
ENGINE = create_engine(DB_URL)
Base.metadata.bind = ENGINE
make_session = sessionmaker(bind=ENGINE)

# --- 3. Kafka Logic ---

def process_messages():
    """ Process event messages from Kafka """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    
    # Create a consumer that reads new messages (uncommitted)
    # reset_offset_on_start=False ensures we pick up where we left off
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    logger.info("Kafka consumer started. Waiting for messages...")

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg_obj = json.loads(msg_str)
        logger.info("Message received: %s" % msg_obj)

        payload = msg_obj["payload"]
        session = make_session()

        try:
            if msg_obj["type"] == "meal": # Match your event type from Receiver
                new_meal = Meal(
                    user_id=payload.get('user_id'),
                    source_device=payload.get('source_device'),
                    meal_id=payload.get('meal_id'),
                    trace_id=payload.get('trace_id'),
                    record_timestamp=datetime.fromisoformat(payload.get('record_timestamp').replace('Z', '+00:00')),
                    batch_timestamp=datetime.fromisoformat(payload.get('batch_timestamp').replace('Z', '+00:00')),
                    calories=payload.get('calories'),
                    meal_type=payload.get('meal_type'),
                    carbs_g=payload.get('carbs_g'),
                    protein_g=payload.get('protein_g'),
                    fat_g=payload.get('fat_g')
                )
                session.add(new_meal)
                logger.debug(f"Stored meal event {payload.get('trace_id')} to DB")

            elif msg_obj["type"] == "exercise": # Match your event type from Receiver
                new_exercise = Exercise(
                    user_id=payload.get('user_id'),
                    trace_id=payload.get('trace_id'),
                    source_device=payload.get('source_device'),
                    exercise_id=payload.get('exercise_id'),
                    record_timestamp=datetime.fromisoformat(payload.get('record_timestamp').replace('Z', '+00:00')),
                    batch_timestamp=datetime.fromisoformat(payload.get('batch_timestamp').replace('Z', '+00:00')),
                    type=payload.get('type'),
                    duration_min=payload.get('duration_min'),
                    avg_heart_rate=payload.get('avg_heart_rate'),
                    peak_heart_rate=payload.get('peak_heart_rate')
                )
                session.add(new_exercise)
                logger.debug(f"Stored exercise event {payload.get('trace_id')} to DB")

            session.commit()
            consumer.commit_offsets() # Tell Kafka we've successfully processed this
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            session.rollback()
        finally:
            session.close()

def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()


def get_session():
    return make_session()

def get_meals_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_timestamp.replace('Z', '+00:00'))
    statement = select(Meal).where(Meal.record_timestamp >= start).where(Meal.record_timestamp < end)
    results = session.execute(statement).scalars().all()
    res_list = [meal.to_dict() for meal in results]
    session.close()
    return res_list, 200

def get_exercise_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_timestamp.replace('Z', '+00:00'))
    statement = select(Exercise).where(Exercise.record_timestamp >= start).where(Exercise.record_timestamp < end)
    results = session.execute(statement).scalars().all()
    res_list = [ex.to_dict() for ex in results]
    session.close()
    return res_list, 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    setup_kafka_thread()
    app.run(port=8090)