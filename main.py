import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import sys
from selenium.common.exceptions import NoSuchElementException

webhook_url = ''
urls = []

if len(sys.argv) > 2:
    # Access individual arguments
    webhook_url = sys.argv[1]
    urls = sys.argv[2:]
else:
    print("No arguments provided.")
    exit()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

while True:
    for i, url in enumerate(urls):
        # Set up the Selenium WebDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the web page
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

        progress = '抓標題'

        try:
            title = driver.find_element(By.CSS_SELECTOR, "div.narrow-wrapper.ng-scope > div > h1").get_attribute('innerText').strip()

            progress = '抓票的欄位'
            # Check if the desired element is present
            elements = driver.find_elements(By.CSS_SELECTOR, "div.ticket-unit.ng-scope")
            available_tickets = [e.get_attribute('innerText').split() for e in elements if (e.get_attribute('innerText').split()[-1] != '已售完' and e.get_attribute('innerText').split()[-1] != '暫無票券')]

            tickets_str = '\n'.join([' '.join(ticket) for ticket in available_tickets])
            logging.info(f'{title} {available_tickets}')

            if len(available_tickets) > 0:
                message = f'{title} 有票!\n\n{tickets_str}\n{urls[i]}'

                # Send the message if the element is found
                response = requests.post(webhook_url, json={"content": message})
                if response.ok:
                    logging.info("Message sent successfully")
                else:
                    logging.warn(f"Failed to send message. Status code:, {response.status_code}")
        except NoSuchElementException:
            message = f'{urls[i]} {progress}發生錯誤!'

            # Send the message if the element is found
            response = requests.post(webhook_url, json={"content": message})

        driver.quit()
        # Wait for some time before refreshing the page
        time.sleep(5)
print("hi")