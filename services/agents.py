from abc import ABC
import logging

from domain.models import (
    Action,
    HeadcountChangeSignal,
    ReportingChangeSignal,
    Signal,
    PressMentionSignal,
)
from openai import OpenAI

LOGGER = logging.getLogger(__name__)


class Agent(ABC):
    def process_signals(self, signals: list[Signal]) -> list[Action]:
        raise NotImplemented()

    def process_signal(self, signals: list[Signal]) -> Action:
        raise NotImplemented()

    def can_handle_signal(self, signal: Signal) -> bool:
        raise NotImplemented()


class ReportSummaryAgent(Agent):
    def __init__(self, openai):
        self.client = openai

    def can_handle_signal(self, signal):
        return isinstance(signal, ReportingChangeSignal)

    def prompt_summary(self, signal: ReportingChangeSignal):
        prompt = f"""
            You're a Venture Capital investor and you just received the following reporting from a portfolio company.
            Summarize it in a few sentences, then highlight anything notable or concerning.

            {signal.title}
            {signal.description}
            {signal.company.name}

            Reporting Details:
            - Revenues: {signal.revenues_new} (old: {signal.revenues_old})
            - Cash EOP: {signal.cash_eop_new} (old: {signal.cash_eop_old})
            - EBITDA: {signal.ebitda_new} (old: {signal.ebitda_old})
            - Runway: {signal.runway_months_new} months (old: {signal.runway_months_old})
            - Staff: {signal.staff_new} (old: {signal.staff_old})
            - Clients: {signal.clients_new} (old: {signal.clients_old})
            - ARR: {signal.arr_new} (old: {signal.arr_old})
        """
        LOGGER.info(f"prompting summary: {prompt}")

        messages = [{"role": "system", "content": prompt}]

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        return completion.choices[0].message.content

    def process_signal(self, signal: Signal) -> Action:
        summary = self.prompt_summary(signal)
        return Action(
            signal=signal,
            title="AI-based reporting analysis",
            description=summary,
            url=None,
            score=1.0,
        )


class EmailTheTeamAgent(Agent):
    def __init__(self, openai):
        self.client = openai

    def can_handle_signal(self, signal):
        return True

    def get_prompt(self, signal: Signal):
        prompt = f"""
        You're a Venture Capital investor and you just received the following signal from a portfolio company.
        
        Signal: {signal.title}
        Description: {signal.description}

        Company Details
        name: {signal.company.name}
        domain: {signal.company.domain}
        description: {signal.company.description}

        The issue now is that team is under pressure in any case.
        Compassion is not helpful here, you need to be direct and to the point.
        The team needs to know that they need to do better and will lose everything if they don't.
        While it may be harsh, it's the only way to get the message across.
        Just return the email draft, nothing else.
        Keep it short and straight to the point.
        """
        return prompt

    def prompt_email(self, signal: Signal):
        prompt = self.get_prompt(signal)
        LOGGER.info(f"prompting email: {prompt}")

        messages = [{"role": "system", "content": prompt}]

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        return completion.choices[0].message.content

    def process_signal(self, signal: Signal) -> Action:
        email = self.prompt_email(signal)

        return Action(
            signal=signal,
            title="Email the team",
            description="Here is an email you could send the team:\n" + email,
            url=None,
            score=1.0,
        )


class PostOnLinkedinAgent(EmailTheTeamAgent):
    def can_handle_signal(self, signal):
        if isinstance(signal, HeadcountChangeSignal):
            return True

        if isinstance(signal, ReportingChangeSignal):
            return True

        return False

    def get_prompt(self, signal):
        prompt = f"""
        You're a Venture Capital investor and you just received the following signal from a portfolio company.

        Signal: {signal.title}
        Description: {signal.description}

        Company Details
        name: {signal.company.name}
        domain: {signal.company.domain}
        description: {signal.company.description}

        You now want to brag about your portfolio company on Linkedin.
        As Linkedin cannot be taken seriously, you want to make the post as cringey as possible.
        Really go all in, however insignificant the achievement is.
        This way, you can share a laugh with your friends and colleagues.
        Just return the Linkedin post, nothing else.
        If possible, start with 'I am humbled and excited to annouce...'
        Keep it short and straight to the point.
        """
        return prompt

    def process_signal(self, signal: Signal) -> Action:
        email = self.prompt_email(signal)

        return Action(
            signal=signal,
            title="Humble-brag on Linkedin",
            description="We got you, here is your Linkedin post:\n" + email,
            url=None,
            score=1.0,
        )


class PressMentionAgent(Agent):
    def get_messages(self, signal: PressMentionSignal) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a professional assistant that evaluates press mention signals for their importance and urgency.",
            },
            {
                "role": "user",
                "content": f"""
                    Based on the details provided below, generate:
                    1. A personalized, engaging notification message to prompt the user to take action.
                    2. A priority score between 0 and 1 (where 1 means extremely high priority and 0 means very low priority).

                    Signal Details:
                    - Title: {signal.title}
                    - Description: {signal.description}
                    - Platform: {signal.plateform}
                    - Source: {signal.source_name}
                    - Engagement Count: {signal.engagement_count}
                    - URL: {signal.url_link}

                    Response format:
                    - Message: "Your personalized message here"
                    - Score: [a number between 0 and 1]
                    """,
            },
        ]

        return messages

    def process_signals(self, signals: list[PressMentionSignal]) -> list[Action]:
        actions = []
        for signal in signals:
            messages = self.get_messages(signal)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )

            output = completion.choices[0].message.content.strip()
            try:
                message, score = output.split("- Score:")
                message = message.replace("- Message:", "").strip()
                score = float(score.strip())
            except ValueError:
                message = "An important mention was detected, but the message couldn't be generated."
                score = 0.5

            action = Action(
                signal=signal,
                title=f"Press Mention: {signal.title}",
                description=message,
                url=signal.url_link,
                score=score,
            )
            actions.append(action)
        return actions
