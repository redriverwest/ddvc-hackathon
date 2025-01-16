import datetime
from pydantic import BaseModel, ConfigDict


class Contact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str


class Company(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    domain: str
    linkedin_url: str | None
    description: str
    industry: str
    location: str
    primary_contact: Contact | None


class Signal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    # signaltype: str
    title: str
    description: str
    company: Company


class HeadcountChangeSignal(Signal):
    headcount_new: int
    headcount_old: int


class FollowerCountChangeSignal(Signal):
    followercount_new: int
    followercount_old: int


class NewBacklinkSignal(Signal):
    backlink_url: str


class NewCompetitorSignal(Signal):
    competitor: Company


class ReportingChangeSignal(Signal):
    revenues_new: float
    cash_eop_new: float
    ebitda_new: float
    runway_months_new: float
    staff_new: float
    clients_new: float
    arr_new: float
    revenues_old: float
    cash_eop_old: float
    ebitda_old: float
    runway_months_old: float
    staff_old: float
    clients_old: float
    arr_old: float


class PressMentionSignal(Signal):
    url_link: str
    plateform: str
    source_name: str
    post_date: datetime.datetime
    # sentiment: str
    engagement_count: int
    # tags: list[str]


class Action(BaseModel):
    signal: Signal
    title: str
    description: str
    url: str | None
    score: float


class EmailAction(Action):
    context_message: str
    email_message: str


class CommentAction(Action):
    context_message: str
    comment_message: str


class ShareOrRepostAction(Action):
    context_message: str
    reaction: str


class Contact(BaseModel):
    name: str
    email: str


class Note(BaseModel):
    """
    A note to be added to a CRM system.
    """

    title: str
    text: str
