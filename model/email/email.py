from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from constants.common_constants import EmailType
from model.entities import Entities
from template.get_template import html_template


class EmailTracker(Entities, discriminator='EmailTracker'):
    # hk: EmailTracker
    # rk: v<version_number>
    lastEmailSent = UnicodeAttribute(null=True)
    dailyEmailCount = NumberAttribute(null=True)


class EmailTrackerIn(BaseModel):
    model_config = ConfigDict(extra='ignore')

    lastEmailSent: Optional[datetime] = Field(None, title='Last email sent')
    dailyEmailCount: Optional[int] = Field(None, title='Daily email count')


class EmailIn(BaseModel):
    model_config = ConfigDict(extra='ignore')

    to: Optional[List[EmailStr]] = Field(None, title='Email address of the recipient')
    cc: Optional[List[EmailStr]] = Field(None, title='CC Email addresses')
    bcc: Optional[List[EmailStr]] = Field(None, title='BCC Email address')
    subject: str = Field(..., title='Subject of the email')
    salutation: str = Field(..., title='Salutation of the email')
    body: List[str] = Field(..., title='Body of the email')
    regards: List[str] = Field(..., title='Regards of the email')
    emailType: EmailType = Field(..., title='Type of the email')
    eventId: Optional[str] = Field(None, title='Event ID of the email')
    isDurianPy: bool = Field(default=True, title='Is this a DURIANPY sent email?')

    @computed_field
    def content(self) -> str:
        return html_template(is_durian_py=self.isDurianPy)
