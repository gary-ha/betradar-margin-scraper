from betradar_scraper import BetradarScraper
from google_sheets_api import GoogleSheetsAPI

betradar_scraper = BetradarScraper()
google_sheets_api = GoogleSheetsAPI()

try:
    br_ids = google_sheets_api.pull_events(google_sheets_api.range_events)
    soccer_uof = google_sheets_api.pull_soccer_uof_codes()
    tennis_uof = google_sheets_api.pull_tennis_uof_codes()
    print(br_ids)
    betradar_scraper.log_in()
    odds = betradar_scraper.scrape_events(br_ids, soccer_uof, tennis_uof)
    print(odds)
    betradar_scraper.quit_selenium()
    google_sheets_api.export_prices(odds)
    print("Done")
except Exception as e:
    try:
        betradar_scraper.quit_selenium()
        print(e)
    except:
        print(e)


