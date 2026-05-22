import requests

player_name = "Lionel Messi"
url = f"http://127.0.0.1:8000/players/search/{player_name}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Success! Response structure:")
        import json
        print(json.dumps(data, indent=2)[:2000]) # print first 2000 chars
    else:
        print(f"Failed with status: {response.status_code}, response: {response.text}")
except Exception as e:
    print(f"Error querying Transfermarkt API: {e}")
