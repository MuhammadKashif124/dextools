import requests
from datetime import datetime, timedelta

def get_liquidity_pools(chain, sort, order, page=0, pageSize=10, api_key="LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"):
    """
    Fetches liquidity pools information from the specified blockchain for the current day.

    :param chain: Blockchain chain ID (e.g., 'ether')
    :param sort: Sorting type (e.g., 'creationTime', 'creationBlock')
    :param order: Sorting order (e.g., 'asc', 'desc')
    :param page: Page number, starting at 0 (default is 0)
    :param pageSize: Result count per page (default is 10)
    :param api_key: API key for authentication
    :return: JSON response containing liquidity pools information
    """
    api_url = f"https://public-api.dextools.io/trial/v2/pool/{chain}"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": api_key
    }
    
    # Get the current date in ISO format
    current_date = datetime.utcnow()
    from_filter = current_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    to_filter = (current_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    
    params = {
        "sort": sort,
        "order": order,
        "from": from_filter,
        "to": to_filter,
        "page": page,
        "pageSize": pageSize
    }
    
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return response.text

# Example usage
chain = "ether"
sort = "creationTime"
order = "asc"
page = 0
pageSize = 10
api_key = "LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"  # Replace with your actual API key

pools_info = get_liquidity_pools(chain, sort, order, page, pageSize, api_key)
print(pools_info)


# Define the API endpoint and the blockchain chain id
api_url = "https://public-api.dextools.io/trial/v2/blockchain/ether"
api_key = "LTDPU71YvP12mpmDZPTVF4p7aJmJTFjg20KkbWAt"  # Replace with your actual API key

# Define the headers including the API key
headers = {
    "accept": "application/json",
    "X-API-KEY": api_key
}

# Make the GET request
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    blockchain_info = response.json()
    print("Blockchain Information:")
    print(blockchain_info)
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print("Response:", response.text)
