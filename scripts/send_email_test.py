import json
from dotenv import load_dotenv
from usecase.email_usecase import EmailUsecase
from model.email import EmailIn
load_dotenv()
def test_email(testEmail = "your_Email_Here@gmail.com"):
    with open('./template/emailTemplate.html', 'r') as template:
        email_usecase = EmailUsecase()
        email = EmailIn(to=testEmail, cc=[], bcc=[], subject="test", content=template.read(), salutation = "test salutation",regards="test regards", body = "\ntest body")
        emaildict = email.dict()
        message_body = json.dumps(emaildict)
        print(message_body)
        email_usecase.send_email(email)