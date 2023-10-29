import json
from dotenv import load_dotenv
from usecase.email_usecase import EmailUsecase
from model.email import EmailIn
load_dotenv()
def test_email(testEmail = "your_email_here.com"):
    with open('./template/emailTemplate.html', 'r') as template:
        email_usecase = EmailUsecase()
        email = EmailIn(
                        to=testEmail, cc=[], bcc=[], 
                        subject="test Subject", content=template.read(), 
                        salutation = "Good day, Mr. Juan,",
                        regards=["Yours Truly,", "Pablo"], 
                        body = ["I hope this message finds you well. I wanted to share some exciting news with you. After months of hard work and dedication, I have been selected for a once-in-a-lifetime opportunity to participate in a groundbreaking research expedition to explore the uncharted depths of the ocean. The team and I will be embarking on this adventure next month, and I couldn't be more thrilled.",
                                "This expedition is not only a personal dream come true but also a significant step towards understanding our planet's mysteries. I will be documenting the entire journey and sharing our findings with the world. It's a tremendous honor and responsibility, and I can't wait to see where this incredible journey will take us.",
                                "I want to express my gratitude for your support and encouragement throughout my endeavors. Your belief in me has been a driving force behind my achievements, and I will carry your positivity and goodwill with me on this incredible voyage.",
                                "I promise to keep you updated on our progress and discoveries, and I can't wait to share this adventure with you. Thank you again for being a part of this journey with me.",
                                "Wishing you all the best and looking forward to catching up when I return!"]
                        )
        emaildict = email.dict()
        message_body = json.dumps(emaildict)
        print(message_body)
        email_usecase.send_email(email)