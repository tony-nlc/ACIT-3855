import logging.config
import yaml
import connexion
import functools
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from connexion import NoContent
from models import Base, Meal, Exercise

# --- 1. Load Configurations ---
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# --- 2. Database Setup ---
datastore = app_config['datastore']
# Using 127.0.0.1 to avoid the socket error we saw earlier
DB_URL = f"mysql+mysqldb://{datastore['user']}:{datastore['password']}@{datastore['hostname']}:{datastore['port']}/{datastore['db']}"
ENGINE = create_engine(DB_URL)
Base.metadata.bind = ENGINE
make_session = sessionmaker(bind=ENGINE)

def use_db_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = make_session()
        try:
            result = func(session, *args, **kwargs)
            return result
        finally:
            session.close()
    return wrapper

# --- 3. Endpoint Functions ---

@use_db_session
def process_meal_batch(session, body):
    # Log the receipt of the event (INFO)
    trace_id=body.get('trace_id')
    logger.info(f"Received event meal_report with a trace id of {trace_id}")
    new_meal = Meal(
        user_id=body.get('user_id'),
        source_device=body.get('source_device'),
        meal_id=body.get('meal_id'),
        trace_id=trace_id,
        record_timestamp=datetime.fromisoformat(body.get('record_timestamp').replace('Z', '+00:00')),
        batch_timestamp=datetime.fromisoformat(body.get('batch_timestamp').replace('Z', '+00:00')),
        calories=body.get('calories'),
        meal_type=body.get('meal_type'),
        carbs_g=body.get('carbs_g'),
        protein_g=body.get('protein_g'),
        fat_g=body.get('fat_g')
    )

    session.add(new_meal)
    session.commit()
    
    # Log the response (INFO)
    logger.info(f"Response for event meal_report (id: {trace_id}) has status 201")
    
    # Successful storage log (DEBUG) - This runs after the session logic is done
    logger.debug(f"Stored event meal_report with a trace id of {trace_id}")

    return NoContent, 201

@use_db_session
def process_exercise_batch(session, body):
    trace_id=body.get('trace_id')
    logger.info(f"Received event exercise_report with a trace id of {trace_id}")
    new_exercise = Exercise(
        user_id=body.get('user_id'),
        trace_id=trace_id,
        source_device=body.get('source_device'),
        exercise_id=body.get('exercise_id'),
        record_timestamp=datetime.fromisoformat(body.get('record_timestamp').replace('Z', '+00:00')),
        batch_timestamp=datetime.fromisoformat(body.get('batch_timestamp').replace('Z', '+00:00')),
        type=body.get('type'),
        duration_min=body.get('duration_min'),
        avg_heart_rate=body.get('avg_heart_rate'),
        peak_heart_rate=body.get('peak_heart_rate')
    )

    session.add(new_exercise)
    session.commit()

    logger.info(f"Response for event exercise_report (id: {trace_id}) has status 201")
    logger.debug(f"Stored event exercise_report with a trace id of {trace_id}")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    # This is the "ignition" for your server
    app.run(port=8090)
