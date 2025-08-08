import os
import requests
import wikipedia
from bs4 import BeautifulSoup

# Companies and their domains
companies = {
    "Holcim": "holcim.com",
    "CEMEX": "cemex.com",
    "Heidelberg Materials": "heidelbergmaterials.com",
    "Anhui Conch": "conch.cn"
}

# Folder for logos
os.makedirs("assets", exist_ok=True)

def fetch_clearbit(name, domain):
    url = f"https://logo.clearbit.com/{domain}"
    r = requests.get(url)
    if r.status_code == 200 and len(r.content) > 1000:
        path = f"assets/{name.replace(' ', '_')}.png"
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Clearbit: {name}")
        return True
    return False

def fetch_wikipedia(name):
    try:
        page = wikipedia.page(name)
        html = requests.get(page.url).text
        soup = BeautifulSoup(html, "html.parser")
        infobox = soup.find("table", {"class": "infobox"})
        if infobox:
            img = infobox.find("img")
            if img:
                img_url = "https:" + img["src"]
                r = requests.get(img_url)
                if r.status_code == 200:
                    ext = img_url.split(".")[-1].split("?")[0]
                    path = f"assets/{name.replace(' ', '_')}.{ext}"
                    with open(path, "wb") as f:
                        f.write(r.content)
                    print(f"✅ Wikipedia: {name}")
                    return True
    except Exception as e:
        print(f"⚠️ Wikipedia failed for {name}: {e}")
    return False

def fetch_seeklogo(name):
    search_url = f"https://seeklogo.com/search?q={name.replace(' ', '+')}"
    html = requests.get(search_url).text
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("img", {"class": "lazy"})
    if link:
        img_url = link.get("data-src") or link.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        r = requests.get(img_url)
        if r.status_code == 200:
            ext = img_url.split(".")[-1].split("?")[0]
            path = f"assets/{name.replace(' ', '_')}.{ext}"
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"✅ SeekLogo: {name}")
            return True
    return False

# Main loop
for name, domain in companies.items():
    if fetch_clearbit(name, domain):
        continue
    elif fetch_wikipedia(name):
        continue
    elif fetch_seeklogo(name):
        continue
    else:
        print(f"❌ No logo found for {name}")
