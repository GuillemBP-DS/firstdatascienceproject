# utils.py

import requests
import time
from datetime import datetime, timezone
from config import *

URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"


def fetch_live_odds(markets):
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": markets,
        "oddsFormat": ODDS_FORMAT,
        "live": "true"
    }

    r = requests.get(URL, params=params)
    if r.status_code != 200:
        print("❌ Error API:", r.text)
        return []

    return r.json()


def estimate_minute(commence_time):
    try:
        start = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        minutes = int((now - start).total_seconds() / 60)
        return max(1, minutes)
    except:
        return "?"


def is_big_competition(match):
    league = (
        match.get("competition", "") or
        match.get("league", "") or
        match.get("sport_title", "")
    )

    return any(big.lower() in league.lower() for big in BIG_COMPETITIONS)


def is_exchange(bookmaker):
    return any(ex.lower() in bookmaker.lower() for ex in EXCHANGES)


def surebet_3way(odds):
    total = sum(1 / o for o in odds.values())
    return total < 1, (1 - total) * 100


def surebet_2way(odd1, odd2):
    total = (1 / odd1) + (1 / odd2)
    return total < 1, (1 - total) * 100


def calculate_stakes(best_odds, total_bank=100):
    """
    Calcula el stake óptimo para una surebet
    Funciona tanto para mercados 2-way como 3-way
    """

    inv_sum = sum(1 / v["odd"] for v in best_odds.values())

    stakes = {}

    for outcome, data in best_odds.items():
        stakes[outcome] = {
            "amount": (total_bank / data["odd"]) / inv_sum,
            "odd": data["odd"],
            "bookmaker": data["bookmaker"]
        }

    return stakes
