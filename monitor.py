import json
import asyncio
import time
import requests

from bs4 import BeautifulSoup
from telegram import Bot
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]

CHAT_ID = os.environ["CHAT_ID"]

URL = "https://ptu.ac.in/placements/placement-drives/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHECK_INTERVAL = 300  # seconds


# -------------------------
# Telegram
# -------------------------

async def send_message(text):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )


# -------------------------
# JSON
# -------------------------

def load_previous():

    try:
        with open("previous.json", "r", encoding="utf8") as f:
            return json.load(f)

    except:
        return []


def save_previous(data):

    with open("previous.json", "w", encoding="utf8") as f:
        json.dump(data, f, indent=4)


# -------------------------
# Scraper
# -------------------------

def fetch_notices():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find("table", class_="posts-data-table")

    rows = table.find("tbody").find_all("tr")

    notices = []

    for row in rows:

        cols = row.find_all("td")

        title = cols[1].get_text(strip=True)

        date = cols[2].get_text(strip=True)

        pdf = ""

        a = cols[3].find("a")

        if a:
            pdf = a["href"]

        notices.append({
            "title": title,
            "date": date,
            "pdf": pdf
        })

    return notices


# -------------------------
# Compare
# -------------------------

async def check():

    previous = load_previous()

    latest = fetch_notices()

    if not previous:

        print("First run.")
        print("Saving current notices...")

        save_previous(latest)

        return

    old_pdfs = {x["pdf"] for x in previous}

    new_items = []

    for notice in latest:

        if notice["pdf"] not in old_pdfs:

            new_items.append(notice)

    if len(new_items) == 0:

        print(time.strftime("%H:%M:%S"), "No new updates.")

        return

    print()

    print("=" * 60)

    print("NEW UPDATES FOUND:", len(new_items))

    print("=" * 60)

    for notice in reversed(new_items):

        message = f"""
🚨 NEW PTU PLACEMENT UPDATE

📌 {notice['title']}

📅 {notice['date']}

📄 PDF:
{notice['pdf']}

🌐 https://ptu.ac.in/placements/placement-drives/
"""

        print(notice["title"])

        await send_message(message)

    save_previous(latest)


# -------------------------
# Main
# -------------------------

async def main():
    print("=" * 60)
    print("PTU Placement Monitor Started")
    print("=" * 60)

    try:
        await check()
        print("✅ Check completed.")

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    asyncio.run(main())