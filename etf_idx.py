from datetime import datetime
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import json
import os
from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client
import requests

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
chrome_options = Options()
options = [
    # "--headless",
    f"--user-agent={user_agent}",
]
for option in options:
    chrome_options.add_argument(option)

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)
url = 'https://www.idx.co.id/primary/EDD/GetEtfMarket?length=9999'
driver.get(url)


wait = WebDriverWait(driver,60)
pre_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
wait.until(lambda driver: pre_element.text.strip() != '')

data = json.loads(pre_element.text)
rows = data.get('data', [])
df = pd.DataFrame(rows)
df.drop(['IntRow'], axis=1, inplace=True)
df.to_csv('etf.csv', index = False)

