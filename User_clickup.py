import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("API_KEY_CLICKUP")

resp = requests.get(
    "https://api.clickup.com/api/v2/user",
    headers={"Authorization": CLICKUP_TOKEN}
)

data = resp.json()

print("Username:", data["user"]["username"])
print("User ID:", data["user"]["id"])
