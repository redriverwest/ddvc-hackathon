from dataclasses import dataclass
import logging
import os
import click
from dotenv import load_dotenv
from openai import OpenAI
from domain.models import Action, Note, Signal
from infrastructure.attio import CRM, Attio
from services.agents import (
    Agent,
    EmailTheTeamAgent,
    PostOnLinkedinAgent,
    ReportSummaryAgent,
)
from services.signals import generate_signals

# use root logger here
LOGGER = logging


class NoActionAgent(Agent):

    def can_handle_signal(self, signal):
        return True

    def process_signal(self, signal: Signal) -> Action | None:
        # can be replaced with options later
        return None


@click.command()
def run():
    attio = Attio(
        access_token=os.environ["ATTIO_ACCESS_TOKEN"],
        collection=os.environ["ATTIO_COLLECTION"],
    )
    crm = CRM(attio)

    openai = OpenAI()

    # get companies from CRM
    companies = list(crm.generate_companies())
    LOGGER.info(f"Found {len(companies)} companies")

    # generate signals for companies
    signals = list(generate_signals(companies))

    # push signals to agents
    results = []

    agents = [
        ReportSummaryAgent(openai),
        EmailTheTeamAgent(openai),
        PostOnLinkedinAgent(openai),
    ]
    for signal in signals:
        actions = []
        for agent in agents:
            if agent.can_handle_signal(signal):
                action = agent.process_signal(signal)
                if action:
                    actions.append(action)
            else:
                LOGGER.info(f"Agent {agent!r} can not handle {signal!r}")

        results.append((signal, actions))

    # push actions back to CRM
    for signal, actions in results:
        # create note for singal
        LOGGER.info(f"pushing actions: {signal} - {actions}")
        note = generate_note_for_signal(signal, actions)
        crm.push_note(signal.company, note)


def generate_note_for_signal(signal: Signal, actions: list[Action]) -> Note:
    lines = (
        "Midas AI detected a new signal for this company:",
        signal.description,
        "\n",
        "## Potential Actions:",
        (
            "\n\n".join(
                f"### {action.title}\n{action.description}" for action in actions
            )
        ),
        "no actions, use humain judgement" if not actions else "",
    )
    text = "\n".join(lines)

    return Note(
        title=f"Signal: {signal.title}",
        text=text,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # load dotenv for cli runs
    load_dotenv()
    run()
