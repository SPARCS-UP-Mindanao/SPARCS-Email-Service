import json
import os

import boto3

from model.email import EmailIn
from usecase.email_usecase import EmailUsecase
from template.get_template import html_template
EMAIL_QUEUE = os.getenv('EMAIL_QUEUE')
SQS = boto3.client('sqs')
email_usecase = EmailUsecase()


def send_email_handler(event, context):
    _ = context
    for record in event['Records']:
        message_body = json.loads(record['body'])
        email = EmailIn(**message_body, content = html_template())
        email_usecase.send_email(email)
        SQS.delete_message(QueueUrl=EMAIL_QUEUE, ReceiptHandle=record['receiptHandle'])
