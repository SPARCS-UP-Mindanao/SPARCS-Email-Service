import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from model.email import EmailIn
from utils.utils import Utils


class EmailUsecase:
    def __init__(self):
        self.sendgrid_api_key = Utils.get_secret(os.getenv('SENDGRID_API_KEY_NAME'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.display_name = 'UP Mindanao SPARCS'
        self.logger = logging.getLogger()

    def create_email(
        self, sender_email: str, to_email: str, subject: str, content: str, cc: str = None, bcc: str = None
    ) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        msg.attach(MIMEText(content, 'plain'))
        return msg

    def send_email(self, email_body: EmailIn):
        email_from = f'{self.display_name} <{self.sender_email}>'
        to_email = email_body.to
        cc_email = email_body.cc
        bcc_email = email_body.bcc
        subject = email_body.subject
        content = email_body.content

        try:
            with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
                server.starttls()
                server.login('apikey', self.sendgrid_api_key)

                msg = self.create_email(
                    sender_email=email_from,
                    to_email=to_email,
                    subject=subject,
                    content=content,
                    cc=cc_email,
                    bcc=bcc_email,
                )
                server.sendmail(email_from, to_email, msg.as_string())

                message = f'Email sent successfully to {to_email}!'
                self.logger.info(message)

        except Exception as e:
            message = f'An error occurred while sending the email: {e}'
            self.logger.error(message)
