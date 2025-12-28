# markets/over_under.py
from utils import surebet_2way

MARKET_NAME = "OVER / UNDER 2.5"

def scan(match):
    best = {
        "Over": {"odd": 0, "bookmaker": None},
        "Under": {"odd": 0, "bookmaker": None}
    }

    for bookmaker in match.get("bookmakers", []):
        book = bookmaker["title"]
        for market in bookmaker.get("markets", []):
            if market["key"] != "totals":
                continue

            for o in market["outcomes"]:
                if o["name"] == "Over 2.5" and o["price"] > best["Over"]["odd"]:
                    best["Over"] = {"odd": o["price"], "bookmaker": book}
                elif o["name"] == "Under 2.5" and o["price"] > best["Under"]["odd"]:
                    best["Under"] = {"odd": o["price"], "bookmaker": book}

    if any(v["odd"] == 0 for v in best.values()):
        return None

    surebet, profit = surebet_2way(
        best["Over"]["odd"],
        best["Under"]["odd"]
    )

    if not surebet:
        return None

    return {
        "market": MARKET_NAME,
        "best": best,
        "profit": profit
    }
