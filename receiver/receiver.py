import connexion
from connexion import NoContent
import httpx
import uuid
import time
import yaml
import logging.config
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    print(app_config)

with open("conf_log.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

def process_meal_batch(body):
    user_id = body.get("user_id")
    device = body.get("source_device")
    batch_ts = body.get("timestamp")
    
    items = body.get("items", [])
    for meal in items:
        # Add the missing batch-level info to the individual item
        meal['user_id'] = user_id
        meal['trace_id'] = str(uuid.uuid4())
        meal['source_device'] = device
        meal['batch_timestamp'] = batch_ts
        # Map 'timestamp' from item to 'record_timestamp' for storage
        meal['record_timestamp'] = meal.pop('timestamp') 
        httpx.post(app_config['eventstore2']['url'], json=meal)
    
    return NoContent, 201

def process_exercise_batch(body):
    # These are the 'global' values from the batch
    user_id = body.get("user_id")
    device = body.get("source_device")
    batch_ts = body.get("timestamp")
    
    items = body.get("items", [])
    
    for exercise in items:

        # Inject the missing 'required' fields for the Storage API
        exercise['user_id'] = user_id
        exercise['trace_id'] = str(uuid.uuid4())
        exercise['source_device'] = device
        exercise['batch_timestamp'] = batch_ts
        
        # Mapping the field name to match 'record_timestamp' in YAML
        if 'timestamp' in exercise:
            exercise['record_timestamp'] = exercise.pop('timestamp')

        # Log exactly what we are about to send to debug the 400
        logger.debug(f"Sending to storage: {exercise}")
        # Send the individual exercise object
        response = httpx.post(app_config['eventstore1']['url'], json=exercise)
        
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
