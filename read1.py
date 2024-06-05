import requests
import logging
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Email configuration
EMAIL_ADDRESS = "m.kashif@tekrevol.com"
EMAIL_PASSWORD = "Kashif@123#"
RECIPIENT_EMAIL = "evenbetter6@gmail.com"

# Read contract addresses from a text file
def read_contract_addresses(filename='contract_addresses.txt'):
    with open(filename, 'r') as file:
        addresses = file.read().splitlines()
    return addresses

# Get token details from TokenSniffer API
def get_token_details(contract_address, api_key="fd6f3f446dbeb3aae4a6fc2f4983c7b231c57d02"):
    url = f"https://tokensniffer.com/api/v2/tokens/1/{contract_address}?apikey={api_key}&include_metrics=true"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    logging.info(f"TokenSniffer API Response Status for {contract_address}: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch data from TokenSniffer API for {contract_address}. Status code: {response.status_code}")
        return None

# Send an email notification
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
        server.quit()
        logging.info(f"Email sent successfully to {RECIPIENT_EMAIL}")
    except Exception as e:
        logging.error(f"Failed to send email. Error: {str(e)}")

# Process each contract address and check score
def process_contract_addresses(filename='contract_addresses.txt'):
    addresses = read_contract_addresses(filename)
    
    for address in addresses:
        logging.info(f"Processing contract address: {address}")
        token_details = get_token_details(address)
        
        if token_details and 'score' in token_details:
            score = token_details['score']
            if score > 49:
                message = f"Contract address: {address}, Score: {score}"
                print(message)
                send_email("High Score Alert", message)
            else:
                logging.info(f"Contract address: {address} has a score of {score}, which is not greater than 49.")
        else:
            logging.error(f"No valid score found for contract address: {address}")
        
        # Sleep to avoid hitting API rate limits
        time.sleep(1)

# Schedule the process to run every 120 seconds
schedule.every(70).seconds.do(process_contract_addresses)

# Main function to start the process
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)