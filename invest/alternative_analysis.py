"""
EXPERIMENTAL: utility do download the # of open position of a given company on linkedin
"""
import os
import re
from datetime import date
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from invest import loader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

root_folder = (os.path.dirname(os.path.normpath(__file__)))



class LinkedinScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.linkedin = self.load_linkedin()
        self.driver = webdriver.Chrome()


    def jobs_url(self, company):
        return f"https://www.linkedin.com/company/{self.linkedin[company]}/jobs/"

    @staticmethod
    def load_linkedin():
        linkedin_df = loader.load_linkedin()
        return (linkedin_df[['SYMBOL', 'linkedin']].dropna()
                                                   .set_index('SYMBOL')
                                                   .to_dict()['linkedin'])

    def connect(self):
        self.driver.get("https://www.linkedin.com/login")
        sleep(3)
        self.driver.find_element(By.ID, "username").send_keys(self.email)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        return self.driver

    @staticmethod
    def get_employees_number(soup):
        s_1 = soup.get_text()
        index = s_1.find('"employeeCount":')
        s_2 = s_1[index + 1 :]
        n_employee = int(
            re.search(r'"employeeCount":(.*?),"callToAction"', s_2).group(1)
        )
        return n_employee

    @staticmethod
    def get_open_jobs(soup):
        s1 = soup.get_text()
        try:
            if ' job openings - find the one for you.' in s1:
                return s1.split(' job openings - find the one for you.')[0].split(" ")[-1]
            elif ' job opening - find the one for you.' in s1:
                return s1.split(' job opening - find the one for you.')[0].split(" ")[-1]
        except:
            return 0

    @staticmethod
    def get_followers(soup):
        s1 = soup.get_text()
        try:
            return int(s1.split(' followers')[0].split('"')[-1].replace(",", ""))
        except:
            try:
                return int(s1.split(' followers')[0].split(' ')[-1].replace(",", ""))
            except Exception as e:
                print(f"ERROR {e}: {e.__doc__}")
                return None

    def scrape(self, company_list : set):
        results = {}
        driver = self.connect()
        for company in company_list:
            print(f"Scraping {company}")
            sleep(5)
            driver.get(self.jobs_url(company))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                results[company] = {
                    "open_jobs": self.get_open_jobs(soup),
                    "followers": self.get_followers(soup),
                }
                print(
                    f"Scraped {company}: {results[company]['open_jobs']} open jobs and {results[company]['followers']} followers!"
                )
                sleep(5)
            except Exception as e:
                print(f"ERROR {e}: {e.__doc__}")
                pass
        return results



if __name__ == "__main__":

    linkedin_credentials = loader.load_yaml('config.yaml')['linkedin']

    my_scraper = LinkedinScraper(linkedin_credentials['email'],
                                 linkedin_credentials['password'])
    employees_dict = my_scraper.scrape(my_scraper.linkedin.keys())

    results = pd.DataFrame(employees_dict).T
    results.to_csv('linkedin_res.csv')
