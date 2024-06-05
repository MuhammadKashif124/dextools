import requests
from datetime import datetime, timedelta
import logging
import schedule
import time
from termcolor import colored
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHAINS = {
    "Ethereum": 1,
    "BSC": 56,
    "Base": 8453,
    "Polygon": 137,
    "Fantom": 250,
    "Arbitrum": 42161,
    "Avalanche": 43114,
    "Cronos": 25,
    "Oasis": 42262
}

def get_liquidity_pools(chain, sort, order, page=0, pageSize=1, api_key="LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"):
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
        return response.text

def check_token_score(chain_id, address, tokensniffer_api_key):
    api_url = f"https://tokensniffer.com/api/v2/tokens/{chain_id}/{address}"
    
    params = {
        "apikey": tokensniffer_api_key,
        "include_metrics": "true",
        "include_tests": "true",
        "include_similar": "true",
        "block_until_ready": "true"
    }

    headers = {
        "accept": "application/json"
    }
    
    response = requests.get(api_url, headers=headers, params=params)
    
    logging.info(f"TokenSniffer Request URL: {response.url}")
    logging.info(f"TokenSniffer API Response Status for {address}: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logging.info(f"TokenSniffer API Response Data for {address}: {data}")
        score = data.get("score", "N/A")
        return score
    else:
        logging.error(f"Failed to fetch data for address {address}. Status code: {response.status_code}")
        return None

def save_scores_to_file(results, filename='contract_scores.txt'):
    with open(filename, 'a') as file:
        for chain, addresses in results.items():
            for address, score in addresses.items():
                file.write(f"{chain} - {address} : {score}\n")

def send_email_notification(subject, body, to_email, from_email, email_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, email_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        logging.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email. Error: {e}")

def check_new_contracts():
    chain = "ether"
    sort = "creationTime"
    order = "desc"
    page = 0
    pageSize = 10
    dextools_api_key = "LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"  # Replace with your actual API key
    tokensniffer_api_key = "fd6f3f446dbeb3aae4a6fc2f4983c7b231c57d02"  # Replace with your actual API key

    pools_info = get_liquidity_pools(chain, sort, order, page, pageSize, dextools_api_key)

    if isinstance(pools_info, dict) and 'data' in pools_info and 'results' in pools_info['data']:
        results = {chain: {} for chain in CHAINS.keys()}
        addresses_to_check = [pool['address'] for pool in pools_info['data']['results']]

        for address in addresses_to_check:
            for chain_name, chain_id in CHAINS.items():
                score = check_token_score(chain_id, address, tokensniffer_api_key)
                  # Wait 15 seconds between each request to respect rate limits
                results[chain_name][address] = score
                if score is not None and isinstance(score, (int, float)) and score > 50:
                    print(colored(f"Address: {address}, Chain: {chain_name}, Score: {score}", 'red'))
                    send_email_notification(
                        subject="High Score Alert!",
                        body=f"High Score Alert! Address: {address}, Chain: {chain_name}, Score: {score}",
                        to_email='evenbetter6@gmail.com',  # Replace with the recipient's email address
                        from_email='m.kashif@tekrevol.com',  # Replace with your Gmail address
                        email_password='Kashif@123#'  # Replace with your Gmail password or app password
                    )
                else:
                    print(f"Address: {address}, Chain: {chain_name}, Score: {score}")
        save_scores_to_file(results)
        print("Scores saved successfully.")
    else:
        print("No liquidity pools found or failed to fetch data.")

# Schedule the job every 5 minutes
schedule.every(1).minutes.do(check_new_contracts)

print("Scheduler started. Checking for new contracts every 5 minutes.")

while True:
    schedule.run_pending()
    time.sleep(1)
