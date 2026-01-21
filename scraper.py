import pandas as pd
import requests
import time
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_CHAT_ID")

EXCEL_FILE = "matches_daily.xlsx"
HISTORY_FILE = "picks_history.csv"

def calculate_ev(h_odds, prob_h):
    """Calculates Expected Value Edge"""
    if h_odds <= 0: return 0
    implied_prob = 1 / h_odds
    edge = (prob_h / 100) - implied_prob
    return round(edge * 100, 2)

def save_to_history(picks):
    if not picks: return
    df_new = pd.DataFrame(picks)
    df_new['scanned_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if os.path.exists(HISTORY_FILE):
        try:
            df_old = pd.read_csv(HISTORY_FILE)
            df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['home', 'away', 'time'])
            df_combined.to_csv(HISTORY_FILE, index=False)
        except: df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, index=False)

def send_telegram(picks):
    if not picks: return
    msg = f"<b>🚀 Wise Analysis: {len(picks)} Picks Found</b>\n\n"
    for p in picks:
        msg += f"🏟 <b>{p['home']} vs {p['away']}</b>\n"
        msg += f"🏆 {p['league']}\n"
        msg += f"📊 Edge: <b>{p['ev_percent']}%</b> | Risk: {p['risk_score']}/10\n\n"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except: pass

def run_scraper():
    url = "https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/dzisiaj"
    raw_matches = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(viewport={"width": 1920, "height": 3000}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=90000) 
            page.wait_for_selector("div.event-card", timeout=30000)

            for _ in range(12): 
                page.mouse.wheel(0, 3000)
                time.sleep(1.0)

            leagues_map = []
            headers = page.query_selector_all(".e2e-section-title")
            for h in headers:
                box = h.bounding_box()
                if box:
                    leagues_map.append({"name": h.inner_text().strip(), "top": box["y"]})

            leagues_map = sorted(leagues_map, key=lambda x: x['top'])
            cards = page.query_selector_all("div.event-card")
            
            for c in cards:
                try:
                    c_box = c.bounding_box()
                    if not c_box: continue
                    match_league = "International / Other"
                    for l in reversed(leagues_map):
                        if c_box["y"] > l["top"]:
                            match_league = l["name"]
                            break

                    home = c.query_selector("div.e2e-event-team1-name").inner_text().strip()
                    away = c.query_selector("div.e2e-event-team2-name").inner_text().strip()
                    match_time = c.query_selector("span.capitalize").inner_text().strip()
                    odds_els = c.query_selector_all("span.odd-button__odd-value span")
                    if len(odds_els) < 3: continue

                    h_val = float(odds_els[0].inner_text().replace(",", "."))
                    x_val = float(odds_els[1].inner_text().replace(",", "."))
                    a_val = float(odds_els[2].inner_text().replace(",", "."))
                    
                    prob_h = round((1 / h_val) * 100, 1)
                    prob_1x = round(((1/h_val) + (1/x_val)) * 100, 1)
                    risk_score = max(1, min(10, round(10 - (a_val / 3), 1)))
                    
                    # NEW: Expected Value Calculation
                    ev_percent = calculate_ev(h_val, prob_h)

                    status = "RISKY"
                    if h_val <= 1.30: status = "ELITE"
                    elif h_val <= 1.55: status = "VALUE"

                    raw_matches.append({
                        "league": match_league, "home": home, "away": away, 
                        "h_odds": h_val, "a_odds": a_val,
                        "prob": prob_h, "prob_1x": prob_1x,
                        "risk_score": risk_score, "status": status, "time": match_time,
                        "ev_percent": ev_percent
                    })
                except: continue
            
            browser.close()
            if raw_matches:
                pd.DataFrame(raw_matches).to_excel(EXCEL_FILE, index=False)
                picks = [m for m in raw_matches if m["status"] in ["ELITE", "VALUE"]]
                save_to_history(picks)
                send_telegram(picks)
                
    except Exception as e: print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_scraper()