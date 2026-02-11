import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from datetime import datetime

# Load Configs
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

# Path to your stats JSON file
STATS_FILE = app_config['datastore']['filename']

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['interval'])
    sched.start()

def populate_stats():
    """ Periodically processing events """
    logger.info("Start Periodic Processing")
    
    # 1. Load current stats from file (or defaults if file doesn't exist)
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    else:
        stats = {
            "num_meals": 0,
            "num_exercises": 0,
            "max_meal_calories": 0,
            "avg_exercise_duration": 0,
            "last_updated": "2020-01-01T00:00:00Z"
        }

    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    last_updated = stats['last_updated']

    # 2. Call Storage Service for NEW events since last_updated
    storage_url = app_config['eventstore']['url']
    
    # Fetch Meals
    meal_res = requests.get(f"{storage_url}/meals?start_timestamp={last_updated}&end_timestamp={current_timestamp}")
    # Fetch Exercises
    ex_res = requests.get(f"{storage_url}/exercises?start_timestamp={last_updated}&end_timestamp={current_timestamp}")

    if meal_res.status_code == 200:
        meals = meal_res.json()
        for m in meals:
            stats['num_meals'] += 1
            if m['calories'] > stats['max_meal_calories']:
                stats['max_meal_calories'] = m['calories']
    
    if ex_res.status_code == 200:
        exercises = ex_res.json()
        for e in exercises:
            # Rolling Average calculation: (Avg * Count + NewValue) / (Count + 1)
            total_duration = (stats['avg_exercise_duration'] * stats['num_exercises']) + e['duration_min']
            stats['num_exercises'] += 1
            stats['avg_exercise_duration'] = total_duration / stats['num_exercises']

    # 3. Update last_updated and save to JSON
    stats['last_updated'] = current_timestamp
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)
    
    logger.info("Periodic processing finished")


def get_health_stats():
    """ Get current statistics """
    logger.info("Request for statistics has started")
    
    # Check if stats file exists
    if not os.path.exists(STATS_FILE):
        logger.error(f"Statistics file {STATS_FILE} does not exist")
        return {"message": "Statistics do not exist"}, 404
    
    # Read statistics from file
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        
        # Log the contents as DEBUG
        logger.debug(f"Statistics content: {stats}")
        
        # Log completion
        logger.info("Request for statistics has completed")
        
        # Return statistics with 200 status
        return stats, 200
        
    except Exception as e:
        logger.error(f"Error reading statistics file: {e}")
        return {"message": "Statistics do not exist"}, 404
    
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
