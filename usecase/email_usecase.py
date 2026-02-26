import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus
from typing import List

import jinja2
from dateutil.parser import parse

from constants.common_constants import CommonConstants, EmailType
from model.email.email import EmailIn, EmailTrackerIn
from model.registrations.registration import RegistrationIn
from repository.email_tracker_repository import EmailTrackersRepository
from repository.registrations_repository import RegistrationsRepository
from utils.logger import logger
from utils.utils import Utils


class EmailUsecase:
    def __init__(self):
        self.sendgrid_api_key = Utils.get_secret(os.getenv('SENDGRID_API_KEY_NAME'))
        self.sendgrid_smtp_host = 'smtp.sendgrid.net'
        self.ses_smtp_username = Utils.get_secret(os.getenv('SES_SMTP_USERNAME_KEY'))
        self.ses_smtp_password = Utils.get_secret(os.getenv('SES_SMTP_PASSWORD_KEY'))
        self.ses_smtp_host = os.getenv('SES_SMTP_HOST')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.display_name = os.getenv('DISPLAY_EMAIL_NAME')
        self.registrations_repository = RegistrationsRepository()
        self.email_tracker_repository = EmailTrackersRepository()
        self.datetime_now = datetime.now(timezone.utc)

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
            msg['To'] = ', '.join(to_email) if len(to_email) > 1 else to_email[0]
        if cc is not None:
            msg['Cc'] = ', '.join(cc) if len(cc) > 1 else cc[0]
        if bcc is not None:
            msg['Bcc'] = ', '.join(bcc) if len(bcc) > 1 else bcc[0]

        msg.attach(MIMEText(content, 'html'))
        return msg

    def send_email(self, email_body: EmailIn):
        j2 = jinja2.Environment()
        email_from = f'{self.display_name} <{self.sender_email}>'
        to_email = email_body.to
        cc_email = email_body.cc or []
        bcc_email = email_body.bcc
        subject = email_body.subject
        frontend_url = os.getenv('FRONTEND_URL')

        # Ensure durianpy.davao@gmail.com is always CCed
        if CommonConstants.DURIANPY_CC_EMAIL not in cc_email:
            cc_email.append(CommonConstants.DURIANPY_CC_EMAIL)

        # Update email_body with the modified CC list
        email_body.cc = cc_email

        htmlTemplate = j2.from_string(email_body.content)
        content = htmlTemplate.render(
            frontend_url=frontend_url,
            salutation=email_body.salutation,
            body=email_body.body,
            regards=email_body.regards,
        )
        msg = self.create_email(
            sender_email=email_from,
            to_email=to_email,
            subject=subject,
            content=content,
            cc=cc_email,
            bcc=bcc_email,
        )

        smtp_service_daily_free_tier_limit = 100
        email_len = 1

        # Calculate the number of emails to send
        status, email_tracker, _ = self.email_tracker_repository.query_email_tracker()
        if status != HTTPStatus.OK:
            event_update = EmailTrackerIn(
                lastEmailSent=self.datetime_now,
                dailyEmailCount=0,
            )
            (
                _,
                email_tracker,
                _,
            ) = self.email_tracker_repository.create_update_email_tracker(
                email_tracker_in=event_update,
            )

        # Check free tier limit refresh time
        last_email_sent = parse(email_tracker.lastEmailSent)
        if last_email_sent.tzinfo is None:
            last_email_sent = last_email_sent.replace(tzinfo=timezone.utc)

        one_day_passed = (self.datetime_now - last_email_sent).days >= 1

        # Check emails sent
        curent_daily_email_count = 0 if one_day_passed else email_tracker.dailyEmailCount
        total_email_count = curent_daily_email_count + email_len
        use_backup_smtp = total_email_count > smtp_service_daily_free_tier_limit

        # Update daily email count
        if one_day_passed:
            event_update = EmailTrackerIn(
                lastEmailSent=self.datetime_now,
                dailyEmailCount=email_len,
            )
            self.email_tracker_repository.create_update_email_tracker(
                email_tracker_entry=email_tracker,
                email_tracker_in=event_update,
            )

        else:
            self.email_tracker_repository.append_email_sent_count(email_tracker_entry=email_tracker)

        # Send emails
        if use_backup_smtp:
            logger.info('Using SendGrid as secondary SMTP')
            self.send_sendgrid_email(
                msg=msg,
                email_from=email_from,
                to_email=to_email,
                email_body=email_body,
            )

        else:
            logger.info('Using AWS SES as primary SMTP')
            self.send_ses_email(
                msg=msg,
                email_from=email_from,
                to_email=to_email,
                email_body=email_body,
            )
            

    def send_sendgrid_email(
        self,
        msg: MIMEMultipart,
        email_from: str,
        to_email: List[str],
        email_body: EmailIn,
    ):
        try:
            with smtplib.SMTP(self.sendgrid_smtp_host, 587) as server:
                server.starttls()
                server.login('apikey', self.sendgrid_api_key)

                # Create list of all recipients (to, cc, bcc) for actual delivery
                all_recipients = to_email.copy()
                if email_body.cc:
                    all_recipients.extend(email_body.cc)
                if email_body.bcc:
                    all_recipients.extend(email_body.bcc)

                # Remove duplicates while preserving order
                all_recipients = list(dict.fromkeys(all_recipients))

                server.sendmail(email_from, all_recipients, msg.as_string())
                if email_body.eventId:
                    self.update_db_success_sent(email_body)

                message = f'Email sent successfully to {to_email} (and CC/BCC recipients) via SendGrid!'
                logger.info(message)

                server.close()

        except Exception as e:
            message = f'An error occurred while sending the email: {e}'
            logger.error(message)

    def send_ses_email(
        self,
        msg: MIMEMultipart,
        email_from: str,
        to_email: List[str],
        email_body: EmailIn,
    ):
        try:
            with smtplib.SMTP(self.ses_smtp_host, 587) as server:
                server.starttls()
                server.login(self.ses_smtp_username, self.ses_smtp_password)

                # Create list of all recipients (to, cc, bcc) for actual delivery
                all_recipients = to_email.copy()
                if email_body.cc:
                    all_recipients.extend(email_body.cc)
                if email_body.bcc:
                    all_recipients.extend(email_body.bcc)

                # Remove duplicates while preserving order
                all_recipients = list(dict.fromkeys(all_recipients))

                server.sendmail(email_from, all_recipients, msg.as_string())
                if email_body.eventId:
                    self.update_db_success_sent(email_body)

                message = f'Email sent successfully to {to_email} (and CC/BCC recipients) via AWS SES!'
                logger.info(message)

                server.close()

        except Exception as e:
            message = f'An error occurred while sending the email: {e}'
            logger.error(message)

    def update_db_success_sent(self, email_body: EmailIn):
        try:
            (
                status,
                registrations,
                message,
            ) = self.registrations_repository.query_registrations_with_email(
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
                    if not registration:
                        continue

                    (
                        status,
                        _,
                        message,
                    ) = self.registrations_repository.update_registration(
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
