import json
import os
import random
import string
import time

from google.cloud import pubsub
from google.oauth2 import service_account

from google.cloud.forseti.services.base.config import ServiceConfig
from google.cloud.forseti.services.inventory.inventory import Inventory
from google.cloud.forseti.services.model.modeller import Modeller


# Load the configuration from environment variables
PROJECT_ID = os.getenv('PROJECT_ID')
SUBSCRIPTION_NAME = os.getenv('PUBSUB_SUBSCRIPTION')

# Load secrets from the kubernetes secret mount
with open(os.getenv('KEY_FILE')) as f:
    KEY_DATA = json.load(f)
with open(os.getenv('DB_CONN_FILE')) as f:
    DB_CONN_STRING = f.read().decode('utf-8')


# Forseti uses the application default credentials, so we'll write the
# target project's key to this path before running Forseti.  Don't
# confuse this with the service account key above, which used to
# subscribe to the pubsub topic!
target_key_filename = '/tmp/gcp_creds.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = target_key_filename


def callback(message):
    try:
        # extract info from pubsub message attributes
        exp = float(message.attributes['exp'])
        project_name = 'projects/%s' % message.attributes['project_id']

        # discard any jobs past their expiration date
        if time.time() > exp:
            message.ack()
            return

        # write the file used for application default credentials
        with open(target_key_filename, 'w') as f:
            f.write(message.data)

        # prepare the forseti configuration
        forseti_config = ServiceConfig(
            '/app/server.yaml',
            DB_CONN_STRING,
            '[::]:50051',
        )
        forseti_config.config.update_configuration()

        # run forseti inventory starting at the target project
        forseti_config.config.inventory_config.root_resource_id = project_name
        inventory = Inventory(forseti_config)
        inventory_index_id = 0

        for i in inventory.create(False, None):
            inventory_index_id = i.inventory_index_id

        # generate a unique name for the model and create it
        rand = ''.join([random.choice(string.ascii_letters) for n in range(5)])
        name = '%d-%s' % (time.time(), rand)
        modeller = Modeller(forseti_config)
        modeller.create_model('inventory', name, inventory_index_id, False)

        # all done!
        message.ack()

    except Exception as e:
        message.ack()
        print('Message will be dropped as the following error has occurred: ', e)
        print(message.attributes)


def main():
    global KEY_DATA
    creds = service_account.Credentials.from_service_account_info(KEY_DATA)

    subscriber = pubsub.SubscriberClient(credentials=creds)
    future = subscriber.subscribe(
        'projects/%s/subscriptions/%s' % (PROJECT_ID, SUBSCRIPTION_NAME),
        callback,
        flow_control=pubsub.types.FlowControl(max_messages=1),
    )

    try:
        future.result()
    except Exception as ex:
        future.cancel()
        raise


if __name__ == '__main__':
    main()
