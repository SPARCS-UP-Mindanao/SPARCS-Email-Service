from dotenv import load_dotenv

from model.email import EmailIn
from constants.common_constants import EmailType
from usecase.email_usecase import EmailUsecase

load_dotenv()


def send_email_test():
    email_usecase = EmailUsecase()

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
        to=['rneljan@gmail.com'],
        subject=subject,
        body=body,
        salutation=salutation,
        regards=regards,
        emailType=EmailType.REGISTRATION_EMAIL,
        eventId="string",
    )
    email_usecase.send_email(email_body)


if __name__ == '__main__':
    try:
        send_email_test()
    except Exception as e:
        print(e)
