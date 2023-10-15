import logging
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

EMAIL_QUEUE = os.getenv('EMAIL_QUEUE')
SQS = boto3.client('sqs')


def create_email(sender_email, to_email, subject, content) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'plain'))
    return msg


def send_email(subject: str, to_email: str, content: str):
    sender_email = os.getenv('SENDER_EMAIL')
    display_name = 'UP Mindanao SPARCS'
    email_from = f"{display_name} <{sender_email}>"
    sendgrid_api_key = os.getenv('SEND_GRID_API_KEY')

    try:
        with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
            server.starttls()
            server.login('apikey', sendgrid_api_key)

            msg = create_email(email_from, to_email, subject, content)
            server.sendmail(email_from, to_email, msg.as_string())

            message = f"Email sent successfully to {to_email}!"
            logger.info(message)

    except Exception as e:
        message = f"An error occurred while sending the email: {e}"
        logger.error(message)


def send_email_handler(event, context):
    _ = context
    for record in event['Records']:
        message_body = json.loads(record['body'])  # Assuming message body is a JSON string

        send_email(**message_body)

        SQS.delete_message(QueueUrl=EMAIL_QUEUE, ReceiptHandle=record['receiptHandle'])
