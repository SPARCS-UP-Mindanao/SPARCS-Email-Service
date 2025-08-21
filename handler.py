import json
import os

import boto3

from model.email.email import EmailIn
from usecase.email_usecase import EmailUsecase
from utils.logger import logger

EMAIL_QUEUE = os.getenv('EMAIL_QUEUE')
SQS = boto3.client('sqs')
email_usecase = EmailUsecase()


def send_email_handler(event, context):
    _ = context
    records = event['Records']
    logger.info(records)
    for record in records:
        message_body = json.loads(record['body'])
        for message in message_body:
            email_in = EmailIn(**message)
            email_usecase.send_email(email_in)

        SQS.delete_message(QueueUrl=EMAIL_QUEUE, ReceiptHandle=record['receiptHandle'])
