import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_URL = os.getenv('QUEUE_URL')
SQS = boto3.client('sqs')


def send_email_handler(event, context):
    _ = context
    for record in event['Records']:
        return