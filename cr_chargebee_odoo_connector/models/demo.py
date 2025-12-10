# import requests
# from requests.auth import HTTPBasicAuth
# import json
#
# # Configuration
# SITE = 'acmeabc-test'  # Replace with your Chargebee site name
# API_KEY = 'test_XnEsN8V2cuD711k4MDilfqVvFcdTTGVIia'  # Replace with your API key
# BASE_URL = f'https://{SITE}.chargebee.com/api/v2'
# HEADERS = {'Accept': 'application/json'}
#
# def fetch_all_business_entities():
#     """
#     Fetches all Business Entities from Chargebee using the REST API.
#     Handles pagination automatically.
#     Returns a list of BE dictionaries.
#     """
#     url = f'{BASE_URL}/business_entities'
#     all_bes = []
#     offset = None
#     limit = 100  # Max per page (Chargebee limit)
#
#     while True:
#         params = {'limit': limit}
#         if offset:
#             params['offset'] = offset
#
#         # Make the GET request
#         response = requests.get(
#             url,
#             auth=HTTPBasicAuth(API_KEY, ''),
#             headers=HEADERS,
#             params=params
#         )
#
#         # Handle errors
#         if response.status_code != 200:
#             raise Exception(f'API Error {response.status_code}: {response.text}')
#
#         data = response.json()
#         print(f"Fetched {len(data.get('list', []))} BEs from this page")
#
#         # Extract BEs
#         for entry in data.get('list', []):
#             be = entry['business_entity']
#             all_bes.append(be)
#             print(json.dumps(be, indent=2))  # Pretty print each BE
#             print('---')  # Separator
#
#         # Check for next page
#         offset = data.get('next_offset')
#         if not offset:
#             break
#
#     print(f'\nTotal Business Entities fetched: {len(all_bes)}')
#     return all_bes
#
# # Run the function
# if __name__ == '__main__':
#     try:
#         business_entities = fetch_all_business_entities()
#         # Optional: Save to file
#         # with open('business_entities.json', 'w') as f:
#         #     json.dump(business_entities, f, indent=2)
#     except Exception as e:
#         print(f'Error: {e}')

import requests
from requests.auth import HTTPBasicAuth
import json

# Configuration
SITE = 'acmeabc-test'  # Replace with your Chargebee site name
API_KEY = 'test_XnEsN8V2cuD711k4MDilfqVvFcdTTGVIia'  # Replace with your API key
BASE_URL = f'https://{SITE}.chargebee.com/api/v2'
HEADERS = {'Accept': 'application/json'}

def fetch_all_business_entities():
    """
    Fetches all Business Entities from Chargebee using the REST API.
    Handles pagination automatically.
    Returns a list of BE dictionaries.
    """
    url = f'{BASE_URL}/items'
    all_bes = []
    offset = None
    limit = 100  # Max per page (Chargebee limit)

    while True:
        params = {'limit': limit}
        if offset:
            params['offset'] = offset

        # Make the GET request
        response = requests.get(
            url,
            auth=HTTPBasicAuth(API_KEY, ''),
            headers=HEADERS,
            params=params
        )

        # Handle errors
        if response.status_code != 200:
            raise Exception(f'API Error {response.status_code}: {response.text}')

        data = response.json()
        print(f"Items Data : ",data)

        # Extract BEs
        for entry in data.get('list', []):
            be = entry['item']
            all_bes.append(be)
            print(json.dumps(be, indent=2))  # Pretty print each BE
            print('---')  # Separator

        # Check for next page
        offset = data.get('next_offset')
        if not offset:
            break

    print(f'\nTotal Business Entities fetched: {len(all_bes)}')
    return all_bes

# Run the function
if __name__ == '__main__':
    try:
        business_entities = fetch_all_business_entities()
        # Optional: Save to file
        # with open('business_entities.json', 'w') as f:
        #     json.dump(business_entities, f, indent=2)
    except Exception as e:
        print(f'Error: {e}')
