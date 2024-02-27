from bs4 import BeautifulSoup
from etfpy import ETF
from tqdm import tqdm
import requests
import json
import pandas as pd

def extract_value_from_html(html_tag, column_name = None):
    soup = BeautifulSoup(html_tag, 'html.parser')
    if column_name == 'symbol':
        value = soup.span.text
    else:
        value = soup.text
    return value

def fetch_etf(offset):

    url = f'''
    https://etfdb.com/data_set/?tm=40273&cond=%7B%22by_country%22%3A34%7D&no_null_sort=\
    &count_by_id=true&limit=25&sort=weighting&order=desc&limit=25&offset={offset}
    '''
    
    response = requests.get(url)
    data = json.loads(response.text)
    total_etf = data['total']
    
    df = pd.DataFrame(data['rows'])
    df['ticker'] = df['symbol'].apply(extract_value_from_html, 'symbol')
    df['etf'] = df['sather_etfs.name'].apply(extract_value_from_html)
    df['etf_database_category'] = df['etf_category'].apply(extract_value_from_html)
    df = df[['ticker','etf','etf_database_category','expense_ratio', 'weighting']]
    print(f'Fetched {len(df)} ETFs from offset {offset}')
    
    return total_etf, df

df = pd.DataFrame()
offset = 0
total_etf = 1

while offset < total_etf:
    total_etf, etf_df = fetch_etf(offset)
    df = pd.concat([df, etf_df], ignore_index = True)
    offset += 25

data = df.to_dict('records')
print(data)

# Get Sectors
processed = []

for etf in tqdm(data):
    
    info = ETF(etf['ticker'])
    
    # Get AUM, Price
    etf['AUM'] = info.info['AUM']
    etf['Price'] = info.info['Price:']
    
    # Get Holdings
    holdings = []
    for symbol in info.holdings:
        holding = symbol
        holding.pop('Url')
        holdings.append(holding)
    
    etf['Holdings'] = holdings
    
    # Get Region Breakdown, Country Breakdown, Sector Breakdown, Asset Allocation
    exposure = info.exposure
    etf['Region Breakdown'] = exposure['Region Breakdown']
    etf['Country Breakdown'] = exposure['Country Breakdown']
    etf['Sector Breakdown'] = exposure['Sector Breakdown']
    etf['Asset Allocation'] = exposure['Asset Allocation']
    
    processed.append(etf)

print(processed)

with open('etf_us.json', 'w') as f:
    json.dump(processed, f)