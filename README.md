# Digikala High-Discount Tracker 🛒📈

An automated Python-based data extraction pipeline designed to monitor Digikala's daily and incredible offers, filtering products with extraordinary discounts (>= 90%) and synchronizing the structured data with Google Sheets via Google Drive/Sheets APIs.

## Key Features
- **Anti-Bot Bypass:** Implements optimized request headers and custom rotation parameters to bypass server-side tracking defenses (WAF).
- **Data Filtration & Sorting:** Automatically cleans raw JSON responses, filters out irrelevant data, and sorts products in descending order based on discount value.
- **Google Sheets Integration:** Utilizes `gspread` and service account authentication for secure, real-time data logging.
- **Automation Ready:** Fully compatible with local automation tools like Windows Task Scheduler or Cron Jobs.

## Project Structure
- `digikala_scraper.py`: Main execution script containing the data pipeline.
- `.gitignore`: Configured to exclude sensitive credentials (`credentials.json`) from the public repository.

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pip install requests gspread google-auth pytz`
3. Place your own Google Cloud Service Account key as `credentials.json` in the root directory.
4. Share your Google Sheet with the Service Account email as an **Editor**.
5. Update the `SHEET_ID` and Digikala endpoint URLs in the script.
6. Run the script: `python digikala_scraper.py`

---
**Developed by:** Farzaneh Mojalli