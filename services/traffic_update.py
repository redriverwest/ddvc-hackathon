import requests
import json
import random

pages = ["linkedin.com", "facebook.com", "twitter.com", "instagram.com"]


def get_social_mentions(
    company_domain="google.com", start_date="2024-12", end_date="2025-01"
):

    url = (
        f"https://api.similarweb.com/v4/website/{company_domain}/traffic-sources/social"
    )

    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "country": "us",
        "main_domain_only": "false",
        "format": "json",
        "limit": 1000000000,
    }

    headers = {"api-key": ""}

    response = requests.request("GET", url, headers=headers, data=payload)

    if "application/json" in response.headers.get("Content-Type", ""):
        data = response.json()
        social_mentions = data.get("social", [])

        social_mentions = [
            mention for mention in social_mentions if mention["page"] in pages
        ]

        social_mentions = {
            mention["page"]: (
                mention["change"]
                if mention["change"] is not None
                else random.randint(-100, 100) / 100
            )  # For demo purposes, we are generating random values
            for mention in social_mentions
        }
        return social_mentions
    else:
        return {}


if __name__ == "__main__":
    last_social_mentions = get_social_mentions("google.com", "2024-01", "2024-03")
    current_social_mentions = get_social_mentions("google.com", "2024-11", "2024-12")
    print(
        "Social Media share update for the period: 2024-01 to 2024-03:",
        json.dumps(last_social_mentions, indent=2),
    )
    print(
        "Social Media share update for the period: 2024-11 to 2024-12:",
        json.dumps(current_social_mentions, indent=2),
    )
