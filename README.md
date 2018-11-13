# Serverless Forseti example

This repo contains some examples to build a serverless version of
Forseti.  There are two parts:

  - a publisher that queues the inventory jobs for Forseti

  - a worker that consumes those jobs and runs the inventory.

It is not a complete, ready to run repository.  A few things
need to be built and provided for your environment.

## For the job publisher

- In `job_publisher/job_publisher.py`:

  - you'll need to retrieve a list of target projects, or else
     hard-code them.

  - you'll also need a mechanism to get a service account key with
     access to the target projects in the job.

- In `job_publisher/job_publisher.yaml`:

  - info for a Cloud Pub/Sub topic that will serve as a work queue.

  - you'll need a service account key with access to publish to a
     Cloud Pub/Sub topic.  This key should be setup as a Kubernetes
     secret.



## For the job worker

- In `job_worker/app/server.yaml`:

  - you'll need to prepare your desired Forseti configuration.  Even
    better, you might modify your Docker image to download it from
    Cloud Storage.

- In `job_worker/job_worker.yaml`:

  - you'll need a service account key with access to a Cloud Pub/Sub
     subscription on the work queue topic.

  - you'll need a service account key with access to Forseti's Cloud
     SQL instance.  It should be setup as a Kubernetes secret.
