# main.py

import time
import sys
from utils import *
from markets import h2h, over_under, btts

sys.stdout.reconfigure(encoding="utf-8")

# =========================
# CONFIGURACIÓN
# =========================

MIN_PROFIT = 1.0
MAX_PROFIT = 8.0
MIN_DURATION = 15
BANK = 100

# =========================
# MEMORIA (anti-spam)
# =========================

surebet_tracker = {}

# =========================
# MENÚ
# =========================

def show_menu():
    print("===================================")
    print("⚙️ CONFIGURACIÓN DEL SCANNER")
    print("===================================")
    print("MERCADOS:")
    print("1️⃣ Match Winner (1X2)")
    print("2️⃣ Over / Under 2.5")
    print("3️⃣ BTTS")
    print("4️⃣ TODOS LOS MERCADOS")
    print("-----------------------------------")
    print("COMPETICIONES:")
    print("5️⃣ SOLO grandes competiciones")
    print("6️⃣ TODAS las competiciones")
    print("===================================")

    market = input("Selecciona mercado (1-4): ").strip()
    leagues = input("Selecciona competiciones (5-6): ").strip()

    return market, leagues


market_choice, league_choice = show_menu()

# =========================
# MERCADOS ACTIVOS
# =========================

MARKET_MAP = {
    "1": [h2h],
    "2": [over_under],
    "3": [btts],
    "4": [h2h, over_under, btts]
}

if market_choice not in MARKET_MAP:
    print("❌ Mercado inválido")
    sys.exit()

markets_to_scan = MARKET_MAP[market_choice]
use_big_only = league_choice == "5"

market_names = ", ".join(m.MARKET_NAME for m in markets_to_scan)

print("\n⚡ LIVE MULTI-MARKET SUREBET SCANNER ⚡")
print(f"🧩 Mercados: {market_names}")
print(f"🏆 Grandes competiciones: {'SI' if use_big_only else 'NO'}\n")

# =========================
# LOOP PRINCIPAL
# =========================

while True:
    matches = fetch_live_odds(["h2h", "totals", "btts"])
    now = time.time()

    print(f"📡 Partidos LIVE analizados: {len(matches)}")

    # Track current surebets to know which ones are still active
    current_surebets = set()
    
    for match in matches:

        if use_big_only and not is_big_competition(match):
            continue

        match_id = match["id"]
        home = match["home_team"]
        away = match["away_team"]
        minute = estimate_minute(match["commence_time"])

        for market in markets_to_scan:

            result = market.scan(match)
            if not result:
                surebet_tracker.pop((match_id, market.MARKET_NAME), None)
                continue

            profit = result["profit"]

            if not (MIN_PROFIT <= profit <= MAX_PROFIT):
                continue

            key = (match_id, market.MARKET_NAME)
            current_surebets.add(key)
            
            best = result["best"]

            if key not in surebet_tracker:
                # Nueva surebet detectada
                surebet_tracker[key] = {
                    "start": now,
                    "alerted": False,
                    "last_seen": now,
                    "home": home,
                    "away": away,
                    "market": result["market"],
                    "profit": profit,
                    "best": best
                }
                continue

            # Actualizar tiempo de última detección
            surebet_tracker[key]["last_seen"] = now
            surebet_tracker[key]["profit"] = profit
            surebet_tracker[key]["best"] = best

            duration = now - surebet_tracker[key]["start"]

            if duration < MIN_DURATION:
                continue

            # Determinar tipo de mensaje
            if not surebet_tracker[key]["alerted"]:
                # Primera alerta
                surebet_tracker[key]["alerted"] = True
                alert_type = "🔥🔥🔥 NUEVA SUREBET ESTABLE 🔥🔥🔥"
            else:
                # Seguimiento de surebet existente
                alert_type = "✅ SUREBET SIGUE OPERATIVA ✅"

            print(f"\n{alert_type}")
            print(f"{home} vs {away}")
            print(f"🧩 Mercado: {result['market']}")
            print(f"⏱️ Minuto: {minute}'")
            print(f"⏳ Duración: {int(duration)}s")
            print(f"💹 Beneficio: {profit:.2f}%\n")

            for k, v in best.items():
                tag = " (EXCHANGE)" if is_exchange(v["bookmaker"]) else ""
                print(f"{k}: {v['odd']} ({v['bookmaker']}){tag}")

            stakes = calculate_stakes(best, BANK)

            print("\n💰 DÓNDE APOSTAR:")
            for k, d in stakes.items():
                print(
                    f"{k}: {d['amount']:.2f}€ "
                    f"en {d['bookmaker']} "
                    f"(cuota {d['odd']})"
                )

    # Limpiar surebets que ya no existen
    keys_to_remove = [key for key in surebet_tracker if key not in current_surebets]
    for key in keys_to_remove:
        if surebet_tracker[key]["alerted"]:
            home = surebet_tracker[key]["home"]
            away = surebet_tracker[key]["away"]
            market = surebet_tracker[key]["market"]
            print(f"\n❌ SUREBET FINALIZADA: {home} vs {away} - {market}")
        surebet_tracker.pop(key, None)

    print(f"\n⏳ Actualizando en {REFRESH_SECONDS}s...\n")
    time.sleep(REFRESH_SECONDS)