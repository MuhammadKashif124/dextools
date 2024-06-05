import requests
from datetime import datetime
import logging
import schedule
import time
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHAINS = {
    "ether": 1,
    "BSC": 56,
}

def get_liquidity_pools(chain, sort, order, page=0, pageSize=5, api_key="LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"):
    api_url = f"https://public-api.dextools.io/trial/v2/pool/{chain}"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": api_key
    }
    
    current_date = datetime.utcnow()
    from_filter = current_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    to_filter = current_date.isoformat() + "Z"
    
    params = {
        "sort": sort,
        "order": order,
        "from": from_filter,
        "to": to_filter,
        "page": page,
        "pageSize": pageSize
    }
    
    response = requests.get(api_url, headers=headers, params=params)
    
    logging.info(f"DEXTools API Response Status: {response.status_code}")
    if response.status_code == 200:
        logging.info(f"DEXTools API Response Data: {response.json()}")
        return response.json()
    else:
        logging.error(f"Failed to fetch data from DEXTools API. Status code: {response.status_code}")
        return None

def save_contract_addresses_to_file(addresses, filename='contract_addresses.txt'):
    if addresses:
        addresses_df = pd.DataFrame(addresses, columns=['ContractAddress'])
        addresses_df.to_csv(filename, index=False, header=False)
        logging.info("Contract addresses saved successfully.")
    else:
        logging.info("No addresses to save.")

def update_contract_addresses():
    chain = "ether"  # Change to the correct chain name if necessary
    sort = "creationTime"
    order = "desc"
    page = 0
    pageSize = 5
    dextools_api_key = "LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"  # Replace with your actual API key

    pools_info = get_liquidity_pools(chain, sort, order, page, pageSize, dextools_api_key)
    if not pools_info or 'data' not in pools_info or 'results' not in pools_info['data']:
        logging.error("No data found in DEXTools API response.")
        return

    addresses_to_save = [
        pool['address']  # Extract the 'address' field correctly from the response
        for pool in pools_info['data']['results']
    ]

    save_contract_addresses_to_file(addresses_to_save)

# Schedule the job every 5 minutes
schedule.every(2).minutes.do(update_contract_addresses)

logging.info("Scheduler started. Checking for new contracts every 5 minutes.")

while True:
    schedule.run_pending()
    time.sleep(1)