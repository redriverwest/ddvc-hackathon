import json
import os
import random
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Import relativedelta
from models import Company, ReportingChangeSignal, Contact

# Define company profiles with consistent growth rates
companies = [
    {
        "name": "FastGrower1",
        "profile": "very_fast_growth",
        "growth_rate": 0.10,
        "domain": "fastgrower1.com",
        "linkedin_url": None,
        "description": "A fast-growing startup.",
        "industry": "Technology",
        "location": "San Francisco",
        "primary_contact": None,
    },
    {
        "name": "FastGrower2",
        "profile": "very_fast_growth",
        "growth_rate": 0.12,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "UpDown1",
        "profile": "up_down",
        "growth_rate": 0,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "UpDown2",
        "profile": "up_down",
        "growth_rate": 0,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "UpDown3",
        "profile": "up_down",
        "growth_rate": 0,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "SlowGrower1",
        "profile": "slow_growth",
        "growth_rate": 0.03,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "SlowGrower2",
        "profile": "slow_growth",
        "growth_rate": 0.02,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "SlowGrower3",
        "profile": "slow_growth",
        "growth_rate": 0.01,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "Decliner1",
        "profile": "declining",
        "growth_rate": -0.05,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
    {
        "name": "Decliner2",
        "profile": "declining",
        "growth_rate": -0.07,
        "domain": "fastgrower2.com",
        "linkedin_url": None,
        "description": "Another fast-growing startup.",
        "industry": "Technology",
        "location": "New York",
        "primary_contact": None,
    },
]

# Files to store data and state within the 'domain' folder
DATA_FILE = os.path.join("domain", "synthetic_startup_data.json")
STATE_FILE = os.path.join("domain", "company_states.json")
SIGNALS_FILE = os.path.join("domain", "ReportingChangeSignal.json")


def initialize_state():
    """Initialize the state for each company."""
    states = {}
    for company in companies:
        # Initialize starting values
        revenue = random.uniform(5000, 10000)
        staff = random.randint(5, 20)
        clients = random.randint(10, 50)
        arr = revenue * 12

        avg_revenue_per_client = revenue / clients  # Assume average revenue per client
        avg_salary_per_staff = random.uniform(
            4000, 8000
        )  # Average monthly salary per staff
        other_expenses_percentage = random.uniform(
            0.1, 0.2
        )  # Other expenses as a percentage of revenue
        other_expenses = other_expenses_percentage * revenue
        salary_expenses = staff * avg_salary_per_staff
        operating_expenses = salary_expenses + other_expenses
        ebitda = revenue - operating_expenses

        # Calculate monthly burn rate (only if EBITDA is negative)
        monthly_burn = -ebitda if ebitda < 0 else 0

        # Ensure burn rate is at least a minimal value to avoid divide by zero
        if monthly_burn == 0:
            monthly_burn = revenue * 0.1  # Assume a minimal burn rate of 10% of revenue

        # Randomly choose initial runway between 6 and 24 months
        initial_runway_months = random.uniform(6, 24)

        # Set initial cash based on desired runway
        cash = monthly_burn * initial_runway_months

        # Initialize state
        states[company["name"]] = {
            "company": company,
            "current_month": 0,
            "date": datetime(2025, 1, 15),
            "revenue": revenue,
            "cash": cash,
            "staff": staff,
            "clients": clients,
            "avg_revenue_per_client": avg_revenue_per_client,
            "avg_salary_per_staff": avg_salary_per_staff,
            "other_expenses_percentage": other_expenses_percentage,
            "funding_rounds": 0,
            "growth_boost_months": 0,
            "defunct": False,
        }
    return states


def load_state():
    """Load the state from the state file, or initialize if the file doesn't exist."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            states = json.load(f)
            # Convert date strings back to datetime objects
            for company_name in states:
                state = states[company_name]
                date_str = state["date"]
                state["date"] = datetime.strptime(date_str, "%Y-%m")
            return states
    else:
        states = initialize_state()
        # Save initial state
        save_state(states)
        return states


def save_state(states):
    """Save the current state to the state file."""
    # Ensure the 'domain' directory exists
    os.makedirs("domain", exist_ok=True)
    # Convert datetime objects to strings for JSON serialization
    serializable_states = {}
    for company_name, state in states.items():
        state_copy = state.copy()
        if isinstance(state_copy["date"], datetime):
            state_copy["date"] = state_copy["date"].strftime("%Y-%m")
        # Keep the full company data
        serializable_states[company_name] = state_copy
    with open(STATE_FILE, "w") as f:
        json.dump(serializable_states, f, indent=4)


def load_data():
    """Load existing data or initialize a new data structure."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    else:
        return {}


def save_data(data):
    """Save the data to the data file."""
    # Ensure the 'domain' directory exists
    os.makedirs("domain", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def generate_next_month(states, data):
    """Generate data for the next month for all companies."""
    for company_name, state in states.items():
        if state["defunct"]:
            continue  # Skip defunct companies

        company = state["company"]
        current_month = state["current_month"]
        date = state["date"] + relativedelta(months=1)
        state["current_month"] += 1
        state["date"] = date

        # Retrieve state variables
        revenue = state["revenue"]
        cash = state["cash"]
        staff = state["staff"]
        clients = state["clients"]
        avg_revenue_per_client = state["avg_revenue_per_client"]
        avg_salary_per_staff = state["avg_salary_per_staff"]
        other_expenses_percentage = state["other_expenses_percentage"]
        funding_rounds = state["funding_rounds"]
        growth_boost_months = state["growth_boost_months"]
        default_growth_rate = company["growth_rate"]

        # Adjust growth rate with minor randomness
        randomness = random.uniform(-0.005, 0.005)  # Minor randomness
        net_growth_rate = default_growth_rate + randomness

        # Apply growth boost after funding round
        if growth_boost_months > 0:
            net_growth_rate += 0.05  # Additional 5% growth boost
            growth_boost_months -= 1
            state["growth_boost_months"] = growth_boost_months

        # Update revenue
        revenue *= 1 + net_growth_rate

        # Update number of clients proportional to revenue
        clients = max(1, int(revenue / avg_revenue_per_client))

        # Update staff proportional to client growth for growing companies
        staff_growth_rate = (
            net_growth_rate * 0.5
        )  # Staff grows at half the rate of revenue
        staff = max(1, int(staff * (1 + staff_growth_rate)))

        # Update expenses
        avg_salary_per_staff *= 1 + random.uniform(
            0.0, 0.02
        )  # Salaries may increase slightly over time
        salary_expenses = staff * avg_salary_per_staff
        other_expenses = (
            other_expenses_percentage * revenue
        )  # Other expenses proportional to revenue
        operating_expenses = salary_expenses + other_expenses
        ebitda = revenue - operating_expenses

        # Update cash
        cash += ebitda  # Cash changes by EBITDA

        # Calculate runway
        monthly_burn = -ebitda if ebitda < 0 else 0
        runway = cash / monthly_burn if monthly_burn > 0 else float("inf")

        # Check if the company is running low on cash (e.g., less than 3 months of runway)
        if runway <= 3 and cash > 0:
            if random.random() <= 0.5:
                # Company raises a new funding round
                funding_amount = random.uniform(500000, 2000000)  # Amount raised
                cash += funding_amount
                funding_rounds += 1
                growth_boost_months = 6  # Boost growth for next 6 months
                state["growth_boost_months"] = growth_boost_months
                print(
                    f"{company_name} raised ${funding_amount:,.2f} in funding on {date.strftime('%Y-%m')}."
                )
            else:
                # Company fails to raise funds and goes defunct
                print(
                    f"{company_name} failed to raise funds and is now defunct on {date.strftime('%Y-%m')}."
                )
                state["defunct"] = True
                continue  # Skip adding data for this month

        # Check if the company has run out of cash
        if cash <= 0:
            print(
                f"{company_name} has run out of cash and is now defunct on {date.strftime('%Y-%m')}."
            )
            state["defunct"] = True
            continue  # Skip adding data for this month

        arr = revenue * 12

        # Prepare data entry
        data_entry = {
            "date": date.strftime("%Y-%m"),
            "revenues": round(revenue, 2),
            "cash_eop": round(cash, 2),
            "ebitda": round(ebitda, 2),
            "runway_months": round(runway, 2) if runway != float("inf") else "infinite",
            "staff": staff,
            "clients": clients,
            "arr": round(arr, 2),
            "funding_rounds": funding_rounds,
        }

        # Append data entry to data
        if company_name not in data:
            data[company_name] = []
        data[company_name].append(data_entry)

        # Update state variables
        state["revenue"] = revenue
        state["cash"] = cash
        state["staff"] = staff
        state["clients"] = clients
        state["avg_salary_per_staff"] = avg_salary_per_staff
        state["funding_rounds"] = funding_rounds

    return states, data


def generate_reporting_change_signals(states, data):
    """Generate ReportingChangeSignal objects for each company and save them to a JSON file."""
    signals = []

    # Load existing signals if the file exists
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, "r") as f:
            existing_signals = json.load(f)
    else:
        existing_signals = []

    for company_name, records in data.items():
        if len(records) >= 2:
            latest_record = records[-1]
            previous_record = records[-2]

            # Handle 'infinite' runway_months
            latest_runway = (
                float("inf")
                if latest_record["runway_months"] == "infinite"
                else latest_record["runway_months"]
            )
            previous_runway = (
                float("inf")
                if previous_record["runway_months"] == "infinite"
                else previous_record["runway_months"]
            )

            # Retrieve company data from state
            state = states[company_name]
            company_data = state["company"]

            company = Company(
                name=company_data["name"],
                domain=company_data["domain"],
                linkedin_url=company_data.get("linkedin_url", None),
                description=company_data["description"],
                industry=company_data["industry"],
                location=company_data["location"],
                primary_contact=company_data.get("primary_contact", None),
            )

            # Create a ReportingChangeSignal object
            signal = ReportingChangeSignal(
                id=str(uuid.uuid4()),
                start_time=datetime.strptime(previous_record["date"], "%Y-%m"),
                end_time=datetime.strptime(latest_record["date"], "%Y-%m"),
                title=f"Reporting Change for {company_name}",
                description=f"Change detected in reporting data for {company_name}.",
                company=company,
                revenues_new=latest_record["revenues"],
                cash_eop_new=latest_record["cash_eop"],
                ebitda_new=latest_record["ebitda"],
                runway_months_new=latest_runway,
                staff_new=latest_record["staff"],
                clients_new=latest_record["clients"],
                arr_new=latest_record["arr"],
                revenues_old=previous_record["revenues"],
                cash_eop_old=previous_record["cash_eop"],
                ebitda_old=previous_record["ebitda"],
                runway_months_old=previous_runway,
                staff_old=previous_record["staff"],
                clients_old=previous_record["clients"],
                arr_old=previous_record["arr"],
            )
            # Serialize signal and append
            serialized_signal = serialize_signal(signal)
            signals.append(serialized_signal)

    # Append new serialized signals to existing signals
    existing_signals.extend(signals)

    # Ensure the 'domain' directory exists
    os.makedirs("domain", exist_ok=True)

    # Save signals to JSON file
    with open(SIGNALS_FILE, "w") as f:
        json.dump(existing_signals, f, indent=4)

    print("ReportingChangeSignal data generated and saved.")


def serialize_signal(signal):
    """Convert signal object to a JSON-serializable dict."""
    signal_dict = signal.model_dump()
    # Convert datetime objects to strings
    signal_dict["start_time"] = signal_dict["start_time"].strftime("%Y-%m")
    signal_dict["end_time"] = signal_dict["end_time"].strftime("%Y-%m")
    # Handle float('inf')
    if signal_dict["runway_months_new"] == float("inf"):
        signal_dict["runway_months_new"] = "infinite"
    if signal_dict["runway_months_old"] == float("inf"):
        signal_dict["runway_months_old"] = "infinite"
    return signal_dict


def get_latest_reporting_change_signal(company_name):
    """Reads the ReportingChangeSignal.json file and returns the latest ReportingChangeSignal object for the given company."""
    signals = []

    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, "r") as f:
            signals_data = json.load(f)

        for signal_data in signals_data:
            if signal_data["company"]["name"] == company_name:
                # Reconstruct datetime fields
                start_time = datetime.strptime(signal_data["start_time"], "%Y-%m")
                end_time = datetime.strptime(signal_data["end_time"], "%Y-%m")

                # Reconstruct the primary_contact
                company_data = signal_data["company"]
                primary_contact_data = company_data.get("primary_contact")
                if primary_contact_data is not None:
                    primary_contact = Contact(
                        name=primary_contact_data["name"],
                        email=primary_contact_data["email"],
                    )
                else:
                    primary_contact = None

                # Reconstruct the company object
                company = Company(
                    name=company_data["name"],
                    domain=company_data.get("domain"),
                    linkedin_url=company_data.get("linkedin_url"),
                    description=company_data.get("description"),
                    industry=company_data.get("industry"),
                    location=company_data.get("location"),
                    primary_contact=primary_contact,
                )

                # Handle 'infinite' values for runway_months
                runway_months_new = (
                    float("inf")
                    if signal_data["runway_months_new"] == "infinite"
                    else float(signal_data["runway_months_new"])
                )
                runway_months_old = (
                    float("inf")
                    if signal_data["runway_months_old"] == "infinite"
                    else float(signal_data["runway_months_old"])
                )

                # Create the ReportingChangeSignal object
                signal = ReportingChangeSignal(
                    id=signal_data["id"],
                    start_time=start_time,
                    end_time=end_time,
                    title=signal_data["title"],
                    description=signal_data["description"],
                    company=company,
                    revenues_new=float(signal_data["revenues_new"]),
                    cash_eop_new=float(signal_data["cash_eop_new"]),
                    ebitda_new=float(signal_data["ebitda_new"]),
                    runway_months_new=runway_months_new,
                    staff_new=float(signal_data["staff_new"]),
                    clients_new=float(signal_data["clients_new"]),
                    arr_new=float(signal_data["arr_new"]),
                    revenues_old=float(signal_data["revenues_old"]),
                    cash_eop_old=float(signal_data["cash_eop_old"]),
                    ebitda_old=float(signal_data["ebitda_old"]),
                    runway_months_old=runway_months_old,
                    staff_old=float(signal_data["staff_old"]),
                    clients_old=float(signal_data["clients_old"]),
                    arr_old=float(signal_data["arr_old"]),
                )
                signals.append(signal)
    else:
        print(f"No signals file found at {SIGNALS_FILE}.")
        return None

    if not signals:
        print(f"No signals found for company '{company_name}'.")
        return None

    # Sort signals by end_time in descending order to get the latest signal
    signals.sort(key=lambda s: s.end_time, reverse=True)
    latest_signal = signals[0]
    return latest_signal


def main():
    # Do not delete the existing state file
    # if os.path.exists(STATE_FILE):
    #     os.remove(STATE_FILE)
    # Load state and data
    states = load_state()
    data = load_data()

    # Generate data for next month
    states, data = generate_next_month(states, data)

    # Save updated state and data
    save_state(states)
    save_data(data)

    # Generate reporting change signals and dump into ReportingChangeSignal.json
    generate_reporting_change_signals(states, data)

    print("Monthly data generated and saved.")


if __name__ == "__main__":
    main()
    object = get_latest_reporting_change_signal("FastGrower1")
