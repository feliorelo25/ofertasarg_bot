import os
import random
import requests
import tweepy

# ===== AUTH X =====
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_SECRET"],
)

# ===== BUSQUEDAS =====
keywords = [
    "taladro inalambrico",
    "aspiradora robot",
    "camara seguridad wifi",
    "set herramientas",
    "organizador cocina",
]

def buscar_producto():
    keyword = random.choice(keywords)

    url = "https://api.mercadolibre.com/sites/MLA/search"
    params = {"q": keyword}

    data = requests.get(url, params=params).json()

    item = random.choice(data["results"])

    titulo = item["title"]
    precio = item["price"]
    link = item["permalink"]

    tweet = f"""
🔥 Hallazgo en Mercado Libre

{titulo}

💰 ${precio}

👉 {link}
"""

    return tweet

tweet = buscar_producto()

client.create_tweet(text=tweet)

print("Tweet publicado:", tweet)
