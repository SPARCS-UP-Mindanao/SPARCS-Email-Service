import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus
from typing import List

import jinja2

from constants.common_constants import EmailType
from model.email import EmailIn
from model.registrations.registration import RegistrationIn
from repository.registrations_repository import RegistrationsRepository
from utils.logger import logger
from utils.utils import Utils


class EmailUsecase:
    def __init__(self):
        self.sendgrid_api_key = Utils.get_secret(os.getenv('SENDGRID_API_KEY_NAME'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.display_name = 'UP Mindanao SPARCS'
        self.registrations_repository = RegistrationsRepository()

    def create_email(
        self,
        sender_email: str,
        subject: str,
        content: str,
        to_email: List[str] = None,
        cc: List[str] = None,
        bcc: List[str] = None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Subject'] = subject

        if to_email is not None:
            msg['To'] = ", ".join(to_email) if len(to_email) > 1 else to_email[0]
        if cc is not None:
            msg['Cc'] = ", ".join(cc) if len(cc) > 1 else cc[0]
        if bcc is not None:
            msg['Bcc'] = ", ".join(bcc) if len(bcc) > 1 else bcc[0]

        msg.attach(MIMEText(content, 'html'))
        return msg

    def send_email(self, email_body: EmailIn):
        j2 = jinja2.Environment()
        email_from = f'{self.display_name} <{self.sender_email}>'
        to_email = email_body.to
        cc_email = email_body.cc
        bcc_email = email_body.bcc
        subject = email_body.subject
        frontend_url = os.getenv('FRONTEND_URL')

        htmlTemplate = j2.from_string(email_body.content)
        content = htmlTemplate.render(
            frontend_url=frontend_url,
            salutation=email_body.salutation,
            body=email_body.body,
            regards=email_body.regards,
        )

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
                self.update_db_success_sent(email_body)

                message = f'Email sent successfully to {to_email}!'
                logger.info(message)
        except Exception as e:
            message = f'An error occurred while sending the email: {e}'
            logger.error(message)

    def update_db_success_sent(self, email_body: EmailIn):
        try:
            status, registrations, message = self.registrations_repository.query_registrations_with_email(
                event_id=email_body.eventId,
                email=email_body.to[0],
            )
            if status != HTTPStatus.OK:
                logger.error(message)
                return

            registration_update_map = {
                EmailType.REGISTRATION_EMAIL.value: RegistrationIn(registrationEmailSent=True),
                EmailType.CONFIRMATION_EMAIL.value: RegistrationIn(confirmationEmailSent=True),
                EmailType.EVALUATION_EMAIL.value: RegistrationIn(evaluationEmailSent=True),
            }
            if update_obj := registration_update_map.get(email_body.emailType):
                for registration in registrations:
                    status, registration, message = self.registrations_repository.update_registration(
                        registration_entry=registration,
                        registration_in=update_obj,
                    )
                    if status != HTTPStatus.OK:
                        logger.error(message)
                        return

                    logger.info(f'[{registration.registrationId}]: Update Registration successful')
        except Exception as e:
            message = f'An error occurred while updating the database: {e}'
            logger.error(message)
            return
