import json
import os

import boto3

from model.email import EmailIn
from usecase.email_usecase import EmailUsecase
from utils.logger import logger

EMAIL_QUEUE = os.getenv('EMAIL_QUEUE')
SQS = boto3.client('sqs')
email_usecase = EmailUsecase()


def send_email_handler(event, context):
    _ = context
    records = event['Records']
    logger.info(records)
    for record in event['Records']:
        message_body = json.loads(record['body'])
        email = EmailIn(**message_body)
        email_usecase.send_email(email)
        SQS.delete_message(QueueUrl=EMAIL_QUEUE, ReceiptHandle=record['receiptHandle'])
