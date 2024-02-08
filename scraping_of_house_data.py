import sys
import time
import datetime as d
import json
from bs4 import BeautifulSoup
import requests
from creds import key
from creds import secret
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def interact_with_page():
    url = 'https://rentola.com/for-rent?location=amsterdam&rent_per=month&rent=0-2000&rooms=1-3&property_types=apartment'

    number_of_times = 0
    while number_of_times != 3:
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        #options.set_preference("network.cookie.cookieBehavior", 2)

        driver = webdriver.Chrome(options=options,
                                  service=Service(ChromeDriverManager().install())
                                  )

        try:
            driver.get(url)
            driver.maximize_window()
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@data-coi-action="reject_all"]')))

            driver.find_element(By.CSS_SELECTOR, 'div.coi-tcf-modal__footer:nth-child(3) > button:nth-child(1)').click()
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="col-sm-4 col-md-4 col-xs-12 col-lg-3 fix"]/div/a/div/div[1]/div[2]/img'))
            )
            driver.find_element(By.XPATH, '//*[@id="order-by-button"]/span[1]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Latest first"]')))
            driver.find_element(By.XPATH, '//div[text()="Latest first"]').click()
            time.sleep(3)

            flats = []
            flat_inf = {}
            for i in range(1, 10):
                driver.find_element(By.XPATH,
                                    f'//div[@class="col-sm-4 col-md-4 col-xs-12 col-lg-3 fix"][{i}]/div/a/div/div[1]/div[2]/img').click()
                wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[2]/div[2]/div[1]/div/div[2]/div[1]/h1/span'))
                )

                details = driver.find_element(By.XPATH, '//h3[text()="About this property"]')
                driver.execute_script("arguments[0].scrollIntoView();", details)
                driver.execute_script("window.scrollBy(0, -100);")
                time.sleep(3)
                current_url = driver.current_url
                resp = requests.get(current_url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                circle_container = soup.find('div', class_='circle-container')
                for circle in circle_container.find_all('div', class_='circle'):
                    key = circle.find_all('span')[0].get_text(strip=True)
                    value = circle.find_all('span')[1].get_text(strip=True)
                    flat_inf[key] = value
                flats.append(flat_inf)
                time.sleep(3)
                driver.back()
                time.sleep(3)
                next_element = driver.find_element(By.XPATH,
                                                   f'//div[@class="col-sm-4 col-md-4 col-xs-12 col-lg-3 fix"][{i + 1}]/div/a/div/div[1]/div[2]/img')
                driver.execute_script("arguments[0].scrollIntoView();", next_element)
                driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(3)
        except Exception as ex:
            driver.close()
            driver.quit()
            number_of_times += 1
        else:
            driver.close()
            driver.quit()
            time.sleep(5)
            return flats
        sys.exit('Error appeared')

def save_data():
    aws_access_key_id = key
    aws_secret_access_key = secret
    bucket_name = 'web-scraping3670333'
    s3_object_key = f'rental/flats_prices_{d.date.today()}.json'
    flats = interact_with_page()
    json_data = json.dumps(flats, indent=2)
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.put_object(Body=json_data, Bucket=bucket_name, Key=s3_object_key)
    return print('Done')

if __name__ == '__main__':
    save_data()

