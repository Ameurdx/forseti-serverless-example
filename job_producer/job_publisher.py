import os
import time

from google.cloud import pubsub

# load configuration from the envionment
PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_NAME = os.getenv('TOPIC_NAME')

# load the list of target projects from an external service
TARGET_PROJECT_IDS = ...


def main():
    global PROJECT_ID, TOPIC_NAME

    publisher = pubsub.PublisherClient()

    for project_id in TARGET_PROJECT_IDS:
        # call out to our internal service for ephemeral credentials
        proj_creds = ...

        publisher.publish(
            'projects/%s/topics/%s' % (PROJECT_ID, TOPIC_NAME),
            proj_creds,
            project_id=project_id,
            exp_time=time.time() + 3600,
        )


if __name__ == '__main__':
    main()
