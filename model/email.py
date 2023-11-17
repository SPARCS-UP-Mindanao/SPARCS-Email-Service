from typing import List, Optional
from template.get_template import html_template
from pydantic import BaseModel, EmailStr, Field


class EmailIn(BaseModel):
    to: Optional[List[EmailStr]] = Field(None, title="Email address of the recipient")
    cc: Optional[List[EmailStr]] = Field(None, title="CC Email addresses")
    bcc: Optional[List[EmailStr]] = Field(None, title="BCC Email address")
    subject: str = Field(..., title="Subject of the email")
    salutation: str = Field(...,title="Salutation of the email")
    content: str = Field(default=html_template())
    body: List[str] = Field(...,title="Body of the email")
    regards: List[str]= Field(..., title="Regards of the email")
