from dotenv import load_dotenv

from constants.common_constants import EmailType
from model.email import EmailIn
from usecase.email_usecase import EmailUsecase

load_dotenv()


def send_email_test():
    email_usecase = EmailUsecase()
    email_data = {"to": ["rneljan@gmail.com"], "cc": None, "bcc": None,
                  "subject": "UXplore Test Registration Confirmation",
                  "salutation": "Good day asdasd,", "body": ["Thank you for registering for the upcoming UXplore Test!",
                                                             "We\'re thrilled to have you join us. If you have any questions or need assistance, please don\'t hesitate to reach out to us. We\'re here to help!",
                                                             "See you soon!"], "regards": ["Best,"],
                  "emailType": "registrationEmail", "eventId": "uxplore-test"}
    event_name = "SPARCS Career Talks 2023"
    subject = f"Thank you for joining {event_name}. Claim your certificate now!"
    claim_certificate_url = "https://techtix.app/career-talks-2023/evaluate"
    salutation = "Good day,"
    body = [
        f"A big thank you for attending {event_name}! Your participation made the event truly special.",
        "To claim your certificate, please fill out the evaluation form below. Your feedback is crucial for us to keep improving.",
        claim_certificate_url,
        "We're excited to see you at future SPARCS events – more great experiences await!",
    ]
    regards = ["Best,", "SPARCS Team"]
    email_body = EmailIn(
        **email_data
    )
    email_usecase.send_email(email_body)


if __name__ == '__main__':
    try:
        send_email_test()
    except Exception as e:
        print(e)
