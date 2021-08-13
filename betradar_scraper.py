from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from decouple import config
import time
from typing import List, Dict
import datetime


class BetradarScraper:
    def __init__(self):
        self.odds_list = []
        self.betradar_url = "https://ctrl.betradar.com/monitoring"
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=self.options, executable_path=config("WEB_DRIVER"))
        self.driver.create_options()

    def log_in(self):
        print("Loading up Selenium Browser...")
        self.driver.get(self.betradar_url)
        print("Loaded up Selenium Browser...")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='username']")))
        username = self.driver.find_element_by_xpath("//*[@id='username']")
        username.send_keys(config('BR_USERNAME'))
        password = self.driver.find_element_by_xpath("//*[@id='password']")
        password.send_keys(config('BR_PASSWORD'))
        sign_in = self.driver.find_element_by_xpath("//*[@id='loginForm']/button")
        sign_in.click()
        time.sleep(5)

    def scrape_events(self, br_ids: list, soccer_uof: list, tennis_uof: list) -> List[dict]:
        for id in br_ids:
            try:
                betradar_url = f"https://ctrl.betradar.com/match/sr:match:{id}/"
                self.driver.get(betradar_url)
                home_team = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-info__home-team"))).text
                away_team = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-info__away-team"))).text
                date = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-info__date"))).text
                time = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-info__time"))).text
                competition = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-overview__header--breadcrumbs"))).text
                current_time = datetime.datetime.now()
                event_time = f"{date} {time}"
                time_difference = datetime.datetime.strptime(event_time, "%d/%m/%y %H:%M") - current_time
                time_difference_hours = int(time_difference.total_seconds() / 60 / 60)

                if competition.split(" / ")[0] == "SOCCER":
                    for code in soccer_uof:
                        betradar_url = f"https://ctrl.betradar.com/match/sr:match:{id}/market-groups/af052198b17646cb/{code}?odds=1&ownOdds=1"
                        self.driver.get(betradar_url)

                        try:
                            market = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-name"))).text

                            try:
                                most_balanced = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "most-balanced-line")))
                                line = most_balanced.find_element_by_class_name('matchup-market-vertical-view-outcome-name').text

                                market_dict = {
                                    "Current Time": current_time.strftime("%d/%m/%y %H:%M"),
                                    "KO Time": f"{date} {time}",
                                    "Time Difference": -1 * time_difference_hours,
                                    "Event": f"{home_team} vs {away_team}",
                                    "Competition": competition,
                                    "Market": f"{market} {line}",
                                }

                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "market-header-bookmaker-name")))
                                bookmakers = self.driver.find_elements_by_class_name("market-header-bookmaker-name")
                                bookmakers_odds = most_balanced.find_elements_by_css_selector("div.bookmaker-key-cell")
                                for i in range(len(bookmakers)):
                                    market_dict[bookmakers[i].text] = bookmakers_odds[i].text
                                self.odds_list.append(market_dict)

                            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                                try:
                                    market_dict = {
                                        "Current Time": current_time.strftime("%d/%m/%y %H:%M"),
                                        "KO Time": f"{date} {time}",
                                        "Time Difference": -1 * time_difference_hours,
                                        "Event": f"{home_team} vs {away_team}",
                                        "Competition": competition,
                                        "Market": f"{market}"
                                    }

                                    WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "market-header-bookmaker-name")))
                                    bookmakers = self.driver.find_elements_by_class_name("market-header-bookmaker-name")
                                    bookmakers_odds_row = WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "market-vertical-line")))
                                    bookmakers_odds = bookmakers_odds_row.find_elements_by_css_selector("div.bookmaker-key-cell")
                                    for i in range(len(bookmakers)):
                                        market_dict[bookmakers[i].text] = bookmakers_odds[i].text
                                    self.odds_list.append(market_dict)
                                except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                                    continue
                        except (NoSuchElementException, TimeoutException):
                            continue

                if competition.split(" / ")[0] == "TENNIS":
                    for code in tennis_uof:
                        betradar_url = f"https://ctrl.betradar.com/match/sr:match:{id}/market-groups/67c420d8e1bc4855/{code}?odds=1&ownOdds=1"
                        self.driver.get(betradar_url)

                        try:
                            market = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "market-name"))).text

                            try:
                                most_balanced = WebDriverWait(self.driver, 1).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "most-balanced-line")))
                                line = most_balanced.find_element_by_class_name(
                                    'matchup-market-vertical-view-outcome-name').text

                                market_dict = {
                                    "Current Time": current_time.strftime("%d/%m/%y %H:%M"),
                                    "KO Time": f"{date} {time}",
                                    "Time Difference": -1 * time_difference_hours,
                                    "Event": f"{home_team} vs {away_team}",
                                    "Competition": competition,
                                    "Market": f"{market} {line}",
                                }

                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "market-header-bookmaker-name")))
                                bookmakers = self.driver.find_elements_by_class_name("market-header-bookmaker-name")
                                bookmakers_odds = most_balanced.find_elements_by_css_selector("div.bookmaker-key-cell")
                                for i in range(len(bookmakers)):
                                    market_dict[bookmakers[i].text] = bookmakers_odds[i].text
                                self.odds_list.append(market_dict)

                            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                                try:
                                    market_dict = {
                                        "Current Time": current_time.strftime("%d/%m/%y %H:%M"),
                                        "KO Time": f"{date} {time}",
                                        "Time Difference": -1 * time_difference_hours,
                                        "Event": f"{home_team} vs {away_team}",
                                        "Competition": competition,
                                        "Market": f"{market}"
                                    }

                                    WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "market-header-bookmaker-name")))
                                    bookmakers = self.driver.find_elements_by_class_name("market-header-bookmaker-name")
                                    bookmakers_odds_row = WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "market-vertical-line")))
                                    bookmakers_odds = bookmakers_odds_row.find_elements_by_css_selector(
                                        "div.bookmaker-key-cell")
                                    for i in range(len(bookmakers)):
                                        market_dict[bookmakers[i].text] = bookmakers_odds[i].text
                                    self.odds_list.append(market_dict)
                                except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                                    continue
                        except (NoSuchElementException, TimeoutException):
                            continue
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                continue
        return self.odds_list

    def quit_selenium(self):
        self.driver.quit()
