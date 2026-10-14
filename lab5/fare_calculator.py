"""Public transit fare calculator and smart-card utilities."""

from decimal import Decimal, ROUND_HALF_UP
import re
from xml.sax.handler import ContentHandler  # nosec B406
import paramiko
from cryptography.hazmat.primitives import hashes
from defusedxml import defuse_stdlib
from defusedxml import sax as defused_sax

# Protect standard-library XML parsers against unsafe XML features.
defuse_stdlib()

# Metro fare rules (fictional city).
DISTANCE_SLABS = [(2, 10), (5, 20), (12, 30), (21, 40), (32, 50)]
MAX_FARE = 60
DAILY_CAP = 150
OFF_PEAK_DISCOUNT = Decimal("0.10")
CONCESSIONS = {"student": Decimal("0.25"), "senior": Decimal("0.50")}
cards = {}


def base_of(km):
    """Return the base fare for a journey of the given distance."""
    return fare_for_distance(km)


def fare_for_distance(km):
    """Return the fare slab for the given distance in kilometres."""
    for limit, fare in DISTANCE_SLABS:
        if km < limit:
            return fare
    return MAX_FARE


def is_peak(time_hhmm):
    """Return whether a time falls within the configured peak hours."""
    hour = int(time_hhmm.split(":")[0])
    return (8 <= hour <= 10) or (17 <= hour <= 20)


def journey_fare(km, time_hhmm, categories=None):
    """Calculate a journey fare after time-based and concession discounts."""
    if categories is None:
        categories = []

    fare = Decimal(str(base_of(km)))
    if not is_peak(time_hhmm):
        fare *= Decimal("1") - OFF_PEAK_DISCOUNT

    for category in categories:
        if category not in CONCESSIONS:
            raise ValueError(f"Unknown concession category: {category}")
        fare *= Decimal("1") - CONCESSIONS[category]

    return fare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def daily_total(journeys):
    """Return the day's fares, limited to the configured daily cap."""
    total = sum(
        (
            journey_fare(km, time_hhmm, categories)
            for km, time_hhmm, categories in journeys
        ),
        Decimal("0"),
    )
    return min(total, Decimal(str(DAILY_CAP)))


def issue_card(card_id, balance=0):
    """Create a smart card with a non-negative starting balance."""
    starting_balance = Decimal(str(balance))
    if starting_balance < 0:
        raise ValueError("Starting balance cannot be negative.")
    cards[card_id] = {"balance": starting_balance, "trips": []}


def tap_out(card_id, km, time_hhmm, categories=None):
    """Charge a smart card for a journey if it has sufficient balance."""
    if categories is None:
        categories = []
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")

    fare = journey_fare(km, time_hhmm, categories)
    balance = cards[card_id]["balance"]
    if balance < fare:
        raise ValueError(
            f"Insufficient balance: fare is Rs.{fare}, "
            f"available balance is Rs.{balance}."
        )

    cards[card_id]["balance"] = balance - fare
    cards[card_id]["trips"].append((km, time_hhmm, fare))
    return cards[card_id]["balance"]


def top_up(card_id, amount):
    """Add a positive amount to a smart card and return its balance."""
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")

    top_up_amount = Decimal(str(amount))
    if top_up_amount <= 0:
        raise ValueError("Top-up amount must be positive.")

    cards[card_id]["balance"] += top_up_amount
    return cards[card_id]["balance"]


def cheapest_route(routes):
    """Return the route distance with the lowest base fare."""
    if not routes:
        raise ValueError("At least one route is required.")
    return min(routes, key=base_of)


def ticket_checksum(ticket_text):
    """Return a SHA-256 checksum for ticket data."""
    digest = hashes.Hash(hashes.SHA256())
    digest.update(ticket_text.encode("utf-8"))
    return digest.finalize().hex()


class StopHandler(ContentHandler):
    """Collect stop names from XML elements named 'stop'."""

    def __init__(self):
        """Initialize the list of stop names."""
        super().__init__()
        self.stops = []

    def startElement(self, name, attrs):
        """Record the name attribute of each stop element."""
        if name == "stop" and "name" in attrs:
            self.stops.append(attrs["name"])


def load_stops(xml_text):
    """Parse XML safely and return the stop names it contains."""
    handler = StopHandler()
    defused_sax.parseString(xml_text.encode("utf-8"), handler)
    return handler.stops


def push_fares_to_gate(gate_host, fare_file):
    """Upload a fare file to a fixed staging path over verified SSH.

    The gate must be configured to process fare_upload.txt in the SFTP
    account's starting directory. The host must be in known_hosts.
    """
    if not re.fullmatch(r"[A-Za-z0-9_./-]+", fare_file):
        raise ValueError("Fare filename contains unsupported characters.")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(gate_host, username="depot")
        sftp = client.open_sftp()
        try:
            sftp.put(fare_file, "fare_upload.txt")
        finally:
            sftp.close()
    finally:
        client.close()


def main():
    """Run a small demonstration of the fare-calculator functions."""
    print("Fare for exactly 2 km:", fare_for_distance(2))
    print("Fare for exactly 32 km:", fare_for_distance(32))
    print("Is 20:45 peak?", is_peak("20:45"))
    print(
        "Student + senior card, 10 km off-peak:",
        journey_fare(10, "14:00", ["student", "senior"]),
    )

    day = [
        (30, "08:15", []),
        (30, "18:30", []),
        (40, "21:00", []),
        (35, "22:30", []),
    ]
    print("Daily total (cap 150):", daily_total(day))

    issue_card("C1", 25)
    try:
        balance = tap_out("C1", 30, "09:00")
        print("Balance after a 30 km trip with Rs.25:", balance)
    except ValueError as error:
        print("Trip declined:", error)

    issue_card("C2", 0)
    print("Top up 0.1 then 0.2:", top_up("C2", 0.1), top_up("C2", 0.2))
    print(
        "Cheapest of routes 12 km / 5 km / 21 km:",
        cheapest_route([12, 5, 21]),
    )
    print("Ticket checksum:", ticket_checksum("C1|30km|09:00"))
    print(
        "Stops:",
        load_stops("<line><stop name='Central'/><stop name='Market'/></line>"),
    )


if __name__ == "__main__":
    main()
