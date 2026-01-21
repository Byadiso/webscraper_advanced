
# ⚽ Betting Smart Dashboard

A high-performance betting analytics suite that scrapes real-time football data,  and calculates **Expected Value (EV)**.

## 🚀 Key Features

* **Real-Time Scraper:** Automated data extraction from Superbet using Playwright.
* **Probability Engine:** Calculates 1X safety buffers and identifies "ELITE" vs "VALUE" picks.
* **Smart Decisions:** Automatically suggests Ultra-Safe Doubles and Hybrid Stability Triples based on risk scores.
* **Investment Calculator:** Allocates daily capital using the **Kelly Criterion** and Anchor/Hybrid strategies.


## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Data Handling:** [Pandas](https://pandas.pydata.org/)
* **Automation:** [Playwright](https://playwright.dev/python/)
* **Notifications:** Telegram Bot API

## 📋 Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Byadiso/webscraper_advanced.git
cd webscraper_advanced

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Install Playwright Browsers:**
```bash
playwright install chromium

```


4. **Configure API (scraper.py):**
Replace the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` with your own credentials to receive mobile alerts.

## 💻 Usage

To launch the dashboard locally, run:

```bash
streamlit run app.py

```

## 🌐 Deployment Notes (Streamlit Cloud)

To deploy successfully on Streamlit Cloud, ensure the following files are present in the root directory:

* `requirements.txt`: Lists all Python libraries.
* `packages.txt`: Contains `libgbm1` and `libasound2` (required for Playwright/Linux).
* `app.py`: The main dashboard file.
* `scraper.py`: The backend scraping engine.

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. Sports betting involves significant risk. Always gamble responsibly.

---
