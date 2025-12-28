# markets/btts.py
from utils import surebet_2way

MARKET_NAME = "BTTS (AMBOS MARCAN)"

def scan(match):
    best = {
        "Yes": {"odd": 0, "bookmaker": None},
        "No": {"odd": 0, "bookmaker": None}
    }

    for bookmaker in match.get("bookmakers", []):
        book = bookmaker["title"]
        for market in bookmaker.get("markets", []):
            if market["key"] != "btts":
                continue

            for o in market["outcomes"]:
                if o["name"] == "Yes" and o["price"] > best["Yes"]["odd"]:
                    best["Yes"] = {"odd": o["price"], "bookmaker": book}
                elif o["name"] == "No" and o["price"] > best["No"]["odd"]:
                    best["No"] = {"odd": o["price"], "bookmaker": book}

    if any(v["odd"] == 0 for v in best.values()):
        return None

    surebet, profit = surebet_2way(
        best["Yes"]["odd"],
        best["No"]["odd"]
    )

    if not surebet:
        return None

    return {
        "market": MARKET_NAME,
        "best": best,
        "profit": profit
    }
