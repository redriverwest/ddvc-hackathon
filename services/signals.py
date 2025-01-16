import datetime
import json
import logging
import random
import typing
from domain.models import (
    Company,
    FollowerCountChangeSignal,
    HeadcountChangeSignal,
    NewBacklinkSignal,
    NewCompetitorSignal,
    PressMentionSignal,
    ReportingChangeSignal,
    Signal,
)

from domain.models import Company, HeadcountChangeSignal, Signal
from services.traffic_update import get_social_mentions

LOGGER = logging.getLogger(__name__)


class SignalProvider:
    """
    A generic class that provides signals for a given company
    """

    def generate_for_company(self, company: Company) -> typing.Iterable[Signal]:
        raise NotImplementedError()


class RandomHeadcountChangeSignalProvider(SignalProvider):
    def generate_for_company(self, company):
        hc_old = random.randint(10, 100)
        hc_new = max(hc_old + random.randint(-10, 10), 0)
        diff = hc_new - hc_old

        return [
            HeadcountChangeSignal(
                id=f"headcount_change_{company.name}",
                start_time=datetime.datetime.now(),
                end_time=datetime.datetime.now(),
                title=f"Headcount {'grew' if diff > 0 else 'shrank'}",
                description=f"The headcount of this company {'grew' if diff > 0 else 'shrank'} from {hc_old} to {hc_new} in the last month",
                company=company,
                headcount_old=hc_old,
                headcount_new=hc_new,
            )
        ]


class RandomBacklinkProvider(SignalProvider):
    def generate_for_company(self, company):
        from services.startupradar import generate_backlinks_for_company

        backlinks = list(generate_backlinks_for_company(company))
        backlink = random.choice(backlinks) if backlinks else None
        if not backlink:
            return []
        signal = NewBacklinkSignal(
            id=f"new_backlink_{company.name}_{backlink['url']}",
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            title=f"New mention: {backlink['domain']}",
            description=f"{company.name} got mentioned here: {backlink['url']}",
            company=company,
            backlink_url=backlink["url"],
        )
        return [signal]


class RandomCompetitorProvider(SignalProvider):
    def generate_for_company(self, company):
        from services.startupradar import generate_competitors

        competitors = list(generate_competitors(company))
        competitor = random.choice(competitors) if competitors else None

        if not competitor:
            return []

        signal = NewCompetitorSignal(
            id=f"new_competitor_{company.name}_{competitor.name}",
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            title=f"New competitor: {competitor.name}",
            description=f"{competitor.name} is a new competitor to {company.name}",
            company=company,
            competitor=competitor,
        )
        return [signal]


class MockCompetitorSignalProvider(SignalProvider):
    def generate_for_company(self, company) -> typing.Iterable[NewCompetitorSignal]:
        # this just returns the current company as competitor
        competitors = [company]

        if competitors:
            competitor = random.choice(competitors)

            signal = NewCompetitorSignal(
                id=f"new_competitor_{company.name}_{competitor.name}",
                start_time=datetime.datetime.now(),
                end_time=datetime.datetime.now(),
                title=f"New competitor: {competitor.name}",
                description=f"{competitor.name} is a new competitor to {company.name}",
                company=company,
                competitor=competitor,
            )
            return [signal]


class TrafficUpdateProvider(SignalProvider):
    def generate_for_company(self, company):
        changes = get_social_mentions(
            company_domain=company.domain, start_date="2024-12", end_date="2025-01"
        )
        print(changes)
        exit()


class CompanyReportSignalProvider(SignalProvider):
    def generate_for_company(self, company):
        signal = ReportingChangeSignal(
            id=f"reporting_change_{company.name}",
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            title="Reporting received",
            description="",
            company=company,
            # data
            revenues_old=900_000,
            revenues_new=1_000_000,
            cash_eop_old=900_000,
            cash_eop_new=800_000,
            ebitda_old=19_000,
            ebitda_new=20_000,
            runway_months_new=8,
            runway_months_old=7,
            staff_old=9,
            staff_new=10,
            clients_old=9,
            clients_new=10,
            arr_old=900_000,
            arr_new=1_000_000,
        )

        # set real description
        description = f"""
            Reporting Details:
            - Revenues: {signal.revenues_new} (old: {signal.revenues_old})
            - Cash EOP: {signal.cash_eop_new} (old: {signal.cash_eop_old})
            - EBITDA: {signal.ebitda_new} (old: {signal.ebitda_old})
            - Runway: {signal.runway_months_new} months (old: {signal.runway_months_old})
            - Staff: {signal.staff_new} (old: {signal.staff_old})
            - Clients: {signal.clients_new} (old: {signal.clients_old})
            - ARR: {signal.arr_new} (old: {signal.arr_old})
        """
        signal.description = description

        return [signal]


def generate_signals(companies: list[Company]) -> typing.Iterable[Signal]:
    signals = []

    for company in companies:
        company_signals = generate_signals_for_company(company)
        LOGGER.info(f"generated {len(company_signals)} signals for {company.name}")

        signals.extend(company_signals)

    return signals


def generate_signals_for_company(company: Company) -> typing.Iterable[Signal]:
    number = random.random()

    if number < 1.0:
        report_provider = CompanyReportSignalProvider()
        return report_provider.generate_for_company(company)
    elif number < 1.0:
        headcount_change_provider = RandomHeadcountChangeSignalProvider()
        return headcount_change_provider.generate_for_company(company)
    elif number < 1.0:
        backlink_provider = RandomBacklinkProvider()
        return backlink_provider.generate_for_company(company)
    else:
        competitor_provider = RandomCompetitorProvider()
        return competitor_provider.generate_for_company(company)


def generate_dummy_signals(companies: list[Company]) -> typing.Iterable[Signal]:
    yield from generate_linkedin_from_file()

    for i in range(1):
        company = Company(
            name=f"company {i}",
            description="very great company",
            domain="example.com",
            industry="example",
            location="Paris, France",
            linkedin_url=None,
            primary_contact=None,
        )

        signal = HeadcountChangeSignal(
            id=str(i),
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            title="",
            description="",
            company=company.model_dump(),
            headcount_old=i,
            headcount_new=i + 5,
        )
        yield signal

        signal = PressMentionSignal(
            id=str(i),
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            title="",
            description="""
                The human papillomavirus (HPV) causes almost all instances of cervical cancer.
                But according to our recent 12-country survey, half the population has a limited understanding of HPV.
                Learn where your country stacks up in its understanding of human papillomavirus (HPV) by reading this report.
                With every HPV test, we grow closer to a world without cervical hashtag#cancer. """,
            company=company.model_dump(),
            url_link="https://www.linkedin.com/feed/?highlightedUpdateType=TRENDING_IN_PAGE_YOU_FOLLOW&highlightedUpdateUrn=urn%3Ali%3Aactivity%3A7282652304695046147",
            plateform="linkedin",
            source_name="Roche",
            post_date=datetime.datetime.now(),
            engagement_count=323,
        )

        yield signal


def generate_linkedin_from_file():
    types = {
        HeadcountChangeSignal: "headcount",
        FollowerCountChangeSignal: "followers",
    }
    for type_, filename in types.items():
        with open(f".data/signals/linkedin/{filename}.json", "r") as fp:
            singals_raw = json.load(fp)
            for signal_raw in singals_raw:
                yield type_.model_validate(signal_raw)


if __name__ == "__main__":
    signals = generate_linkedin_from_file()
    # signals = generate_signals([])
    # for signal in signals:
    #     print(signal)
