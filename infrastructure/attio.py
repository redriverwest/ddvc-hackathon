import json
import logging
import os
import requests

from domain.models import Company, Note


class Attio:
    def __init__(self, access_token: str, collection: str):
        # set up access key
        # https://app.attio.com/apistemic/settings/developers/apps/6c78f4c6-671a-4300-9f9c-723c80ba4a14

        self.access_token = access_token
        self.collection = collection

    def get_lists(self):
        url = "https://api.attio.com/v2/lists"
        resp = self._get(url)

    def get_entries(self):
        url = f"https://api.attio.com/v2/lists/{self.collection}/entries/query"
        resp = self._post(url)
        return resp.json()["data"]

    def get_company(self, company_id):
        url = f"https://api.attio.com/v2/objects/companies/records/{company_id}"
        resp = self._get(url)
        return resp.json()["data"]

    def _get(self, url):
        return requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"}, timeout=10
        )

    def _post(self, url, data=None):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        return requests.post(url, headers=headers, json=data, timeout=10)


class AttioCompany(Company):
    attio_data: dict = None

    @classmethod
    def from_data(cls, data):
        return AttioCompany(
            name=data["values"]["name"][0]["value"],
            description="-",
            domain=data["values"]["domains"][0]["root_domain"],
            linkedin_url=data["values"]["linkedin"][0]["value"],
            industry="unknown",
            location="unknown",
            primary_contact=None,
            attio_data=data,
        )


LOGGER = logging.getLogger(__name__)


class CRM:
    def __init__(self, attio: Attio):
        self.attio = attio

    def get_company(self, company_id) -> AttioCompany:
        company_data = self.attio.get_company(company_id)
        # print(json.dumps(company_data, indent=2))
        return AttioCompany.from_data(company_data)

    def generate_companies(self):
        entries = self.attio.get_entries()
        LOGGER.info(f"Found {len(entries)} companies")

        for entry in entries:
            company_id = entry["parent_record_id"]
            LOGGER.info(f"Processing company {company_id}")
            yield self.get_company(company_id)

    def push_note(self, company: AttioCompany, note: Note):
        url = "https://api.attio.com/v2/notes"

        payload = {
            "data": {
                "format": "plaintext",
                "parent_object": company.attio_data["id"]["object_id"],
                "parent_record_id": company.attio_data["id"]["record_id"],
                "title": note.title,
                "content": note.text,
            }
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.attio.access_token}",
        }

        response = requests.post(url, json=payload, headers=headers)
        # print(response.json())
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # this pushes a test note
    crm = CRM()
    companies = list(crm.generate_companies())
    for company in companies:
        # print(company)
        crm.push_note(company, "This is a test note")
