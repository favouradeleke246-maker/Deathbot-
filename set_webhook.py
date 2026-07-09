import os
import requests

TOKEN = "8799832919:AAFCq-ODuZLu8ebX8kL2As0Q9PqodHabYH8"  # replace or set env
RAILWAY_URL = "https://bountiful-kindness-deathbot.up.railway.app"  # your actual URL
url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={RAILWAY_URL}/webhook"
resp = requests.get(url)
print(resp.json())
