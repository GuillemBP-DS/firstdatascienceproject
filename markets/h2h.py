# markets/h2h.py
from utils import surebet_3way

MARKET_NAME = "MATCH WINNER (1X2)"

def scan(match):
    best = {
        "Home": {"odd": 0, "bookmaker": None},
        "Draw": {"odd": 0, "bookmaker": None},
        "Away": {"odd": 0, "bookmaker": None}
    }

    home = match["home_team"]
    away = match["away_team"]

    for bookmaker in match.get("bookmakers", []):
        book = bookmaker["title"]
        for market in bookmaker.get("markets", []):
            if market["key"] != "h2h":
                continue

            for o in market["outcomes"]:
                if o["name"] == home and o["price"] > best["Home"]["odd"]:
                    best["Home"] = {"odd": o["price"], "bookmaker": book}
                elif o["name"] == away and o["price"] > best["Away"]["odd"]:
                    best["Away"] = {"odd": o["price"], "bookmaker": book}
                elif o["name"] == "Draw" and o["price"] > best["Draw"]["odd"]:
                    best["Draw"] = {"odd": o["price"], "bookmaker": book}

    if any(v["odd"] == 0 for v in best.values()):
        return None

    surebet, profit = surebet_3way({
        k: best[k]["odd"] for k in best
    })

    if not surebet:
        return None

    return {
        "market": MARKET_NAME,
        "best": best,
        "profit": profit
    }
