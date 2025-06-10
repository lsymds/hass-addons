import os
import json
import logging
import requests
from datetime import datetime
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from uk_bin_collection.uk_bin_collection.collect_data import UKBinCollectionApp
from councils import councils

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ukbincollectiondata")

# Home Assistant API settings
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
SUPERVISOR_API_URL = "http://supervisor/core/api/states"

# Selenium settings
SELENIUM_URL = "localhost"
SELENIUM_PORT = 4444

def app():
    # Get configuration from environment variables
    postcode = os.environ.get('POSTCODE')
    schedule = os.environ.get('SCHEDULE', '0 */12 * * *')
    council_id = os.environ.get('COUNCIL')
    council_override_url = os.environ.get('COUNCIL_OVERRIDE_URL', '')
    house_number = os.environ.get('HOUSE_NUMBER')
    uprn = os.environ.get('UPRN')

    logger.info("Starting UK Bin Collection Data addon")
    logger.debug("Configuration: schedule=%s", schedule)

    # Look up the council details and validate URL requirements
    council = councils.get(council_id)
    if not council:
        logger.error(f"Unknown council ID: {council_id}")
        return

    council_name = council["name"]
    council_url = council_override_url if council_override_url else council["url"]

    if council["requires_url_override"] and not council_override_url:
        logger.error(f"Council {council_name} requires a URL override but none was provided. "
                    "Please set the council_override_url configuration option.")
        return

    # Start the scheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(
        lambda: action(council_id, council_url, postcode, house_number, uprn),
        CronTrigger.from_crontab(schedule)
    )

    # Run initial collection
    logger.info("Running initial collection")
    action(council_id, council_url, postcode, house_number, uprn)

    # Start the scheduler
    logger.info("Starting scheduler with schedule: %s", schedule)
    scheduler.start()

def action(council_id, council_url, postcode, house_number, uprn):
    """
    Queries bin collection days and persists them within Home Assistant sensors.
    """
    try:
        # Create args list for the UKBinCollectionApp
        args = [council_id, council_url, '-s']

        if postcode:
            args.extend(['-p', postcode])
        if house_number:
            args.extend(['-n', house_number])
        if uprn:
            args.extend(['-u', uprn])

        args.extend(['-w', f'http://{SELENIUM_URL}:{SELENIUM_PORT}/wd/hub'])

        logger.debug("Calling UKBinCollectionApp with args: %s", ' '.join(args))

        # Create and run the app
        app = UKBinCollectionApp()
        app.set_args(args)
        result = app.run()

        if result is None:
            logger.error("App returned None result")
            return

        collections = json.loads(result)["bins"]
        logger.debug("Received %d collection(s)", len(collections))

        # Process next collection
        if collections:
            next_collection = collections[0]
            collection_date = parser.parse(next_collection['collectionDate']).date()
            days_until = (collection_date - datetime.now().date()).days

            logger.info("Next collection: %s in %d days", next_collection['type'], days_until)
            update_sensor('next_collection', {
                'type': next_collection['type'],
                'colour': next_collection.get('colour', ''),
                'days_until': days_until,
                'date': next_collection['collectionDate'],
                'human_readable_date': collection_date.strftime('%A, %d %B %Y')
            })

            # Process each bin type
            bin_types = {}
            for collection in collections:
                bin_type = collection['type'].lower().replace(" ", "_")
                if bin_type not in bin_types:
                    collection_date = parser.parse(collection['collectionDate']).date()
                    days_until = (collection_date - datetime.now().date()).days
                    bin_types[bin_type] = {
                        'type': collection['type'],
                        'colour': collection.get('colour', ''),
                        'next_collection_days_until': days_until,
                        'next_collection_date': collection['collectionDate'],
                        'next_collection_human_readable_date': collection_date.strftime('%A, %d %B %Y')
                    }
                    logger.debug("Updating sensor for bin type: %s", bin_type)
                    update_sensor(f'bin_{bin_type}', bin_types[bin_type])

    except Exception as e:
        logger.exception("Error fetching bin collection data: %s", str(e))

def update_sensor(sensor_id, state):
    """
    Updates a Home Assistant sensor with the given state.

    Args:
        sensor_id (str): The ID of the sensor to update
        state (dict): The state data to set for the sensor
    """
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN environment variable not set")
        return

    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

    # Create a friendly name from the sensor_id
    friendly_name = " ".join(word.capitalize() for word in sensor_id.replace('_', ' ').split())

    # Extract the main state value based on the sensor type
    if 'days_until' in state:
        state_value = state['days_until']
    else:
        state_value = state.get('next_collection_days_until', 'unknown')

    # Prepare the sensor attributes with metadata
    attributes = {
        "friendly_name": friendly_name,
        "icon": "mdi:trash-can",
        "state_class": "measurement",
        "last_updated": datetime.now().isoformat(),
    }
    attributes.update(state)  # Add all the state data as attributes

    # The entity_id for the sensor
    entity_id = f"sensor.bin_collection_{sensor_id}"

    # Prepare the sensor state data
    sensor_data = {
        "state": state_value,
        "attributes": attributes
    }

    try:
        logger.debug("Updating sensor %s with state %s", entity_id, state_value)

        # Update the sensor state
        response = requests.post(
            f"{SUPERVISOR_API_URL}/{entity_id}",
            headers=headers,
            json=sensor_data
        )

        if not response.ok:
            logger.error("Error updating sensor %s: %s - %s", entity_id, response.status_code, response.text)
        else:
            logger.info("Successfully updated sensor %s", entity_id)

    except requests.exceptions.RequestException as e:
        logger.exception("Error updating sensor %s: %s", entity_id, str(e))

if __name__ == "__main__":
    app()
