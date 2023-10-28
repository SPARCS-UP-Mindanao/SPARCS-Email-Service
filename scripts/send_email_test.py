import json
from dotenv import load_dotenv
from usecase.email_usecase import EmailUsecase
from model.email import EmailIn
load_dotenv()
def test_email(testEmail = "test@gmail.com"):
    with open('./template/emailTemplate.html', 'r') as template:
        email_usecase = EmailUsecase()
        email = EmailIn(to=testEmail, cc=[], bcc=[], subject="test", content=template.read())
        emaildict = email.dict()
        message_body = json.dumps(emaildict)
        print(message_body)
        email_usecase.send_email(email)