from dotenv import load_dotenv

from model.email.email import EmailIn
from usecase.email_usecase import EmailUsecase

load_dotenv()


def send_email_test():
    email_usecase = EmailUsecase()
    email_data = {
        "to": ["rneljan@gmail.com"],
        "cc": None,
        "bcc": None,
        "subject": "UXplore Test Registration Confirmation",
        "salutation": "Good day asdasd,",
        "body": [
            "Thank you for registering for the upcoming UXplore Test!",
            "We\'re thrilled to have you join us. If you have any questions or need assistance, please don\'t hesitate to reach out to us. We\'re here to help!",
            "See you soon!",
        ],
        "regards": ["Best,"],
        "emailType": "registrationEmail",
        "eventId": "uxplore-test",
        "useBackupSMTP": False,
    }
    email_body = EmailIn(**email_data)
    email_usecase.send_email(email_body)


if __name__ == '__main__':
    try:
        send_email_test()
    except Exception as e:
        print(e)
