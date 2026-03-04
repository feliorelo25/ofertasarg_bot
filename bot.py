import os
import random
import requests
import tweepy
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# ========= CONFIG =========
ML_SITE = "MLA"
KEYWORDS = [
    "taladro inalambrico",
    "aspiradora robot",
    "camara seguridad wifi",
    "set herramientas",
    "organizador cocina",
    "mueble industrial",
    "lampara led",
]
RESULTS_LIMIT = 40

# Tu ID de afiliado (matt_tool)
AFFILIATE_MATT_TOOL = "88116574"
# Opcional: tu "matt_word" (en tu ejemplo aparece "ofertasarg")
AFFILIATE_MATT_WORD = "ofertasarg"

# ========= AUTH X =========
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_SECRET"],
)

def add_affiliate_params(url: str) -> str:
    """
    Agrega matt_tool (y matt_word opcional) al link, preservando el #fragment.
    Si ya existen, los reemplaza.
    """
    parts = urlsplit(url)  # scheme, netloc, path, query, fragment
    qs = dict(parse_qsl(parts.query, keep_blank_values=True))

    qs["matt_tool"] = AFFILIATE_MATT_TOOL
    if AFFILIATE_MATT_WORD:
        qs["matt_word"] = AFFILIATE_MATT_WORD

    new_query = urlencode(qs, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

def ml_search(keyword: str) -> dict:
    url = f"https://api.mercadolibre.com/sites/{ML_SITE}/search"
    r = requests.get(url, params={"q": keyword, "limit": RESULTS_LIMIT}, timeout=20)
    r.raise_for_status()
    return r.json()

def pick_item(results: list[dict]) -> dict:
    # Elegimos uno que tenga permalink y price sí o sí
    valid = [it for it in results if it.get("permalink") and it.get("price")]
    if not valid:
        raise RuntimeError("No valid items (missing permalink/price).")
    return random.choice(valid)

def fmt_ars(n) -> str:
    try:
        return f"${int(n):,}".replace(",", ".")
    except Exception:
        return f"${n}"

def build_tweet(item: dict, keyword: str) -> str:
    title = item.get("title", "Producto")
    price = item.get("price")
    link = item.get("permalink")

    aff_link = add_affiliate_params(link)

    # Evitar tweets demasiado largos
    # (X cuenta links como t.co, pero igual mantengámoslo corto)
    tweet = (
        "🔥 Hallazgo en Mercado Libre 🇦🇷\n\n"
        f"{title}\n"
        f"💰 {fmt_ars(price)}\n\n"
        f"👉 {aff_link}\n"
        f"🔎 {keyword}"
    )
    return tweet[:275]  # margen

def main():
    keyword = random.choice(KEYWORDS)
    data = ml_search(keyword)

    results = data.get("results")
    if not isinstance(results, list) or len(results) == 0:
        # Log útil en GitHub Actions si ML cambia algo o responde error "lógico"
        raise RuntimeError(
            f"ML response without results. keyword={keyword} keys={list(data.keys())} sample={str(data)[:500]}"
        )

    item = pick_item(results)
    tweet = build_tweet(item, keyword)

    client.create_tweet(text=tweet)
    print("Tweet publicado:\n", tweet)

if __name__ == "__main__":
    main()
