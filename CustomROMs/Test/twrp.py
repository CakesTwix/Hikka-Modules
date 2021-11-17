from requests import get
from bs4 import BeautifulSoup

def getContent(device):
    twrp_api = "https://dl.twrp.me/"
    url = get(f"{twrp_api}{device}/")

    if url.status_code == 404:
        reply = f"`Couldn't find twrp downloads for {device}!`\n"
        return

    page = BeautifulSoup(url.content, "lxml")
    download = page.find("table").find_all("tr")
    reply = f"**Team Win Recovery Project for {device}:**\n"
    for item in download:
        dl_link = f"https://dl.twrp.me{item.find('a')['href']}"
        dl_file = item.find('td').text
        size = item.find("span", {"class": "filesize"}).text
        reply += (f"⦁ <a href={dl_link}>{dl_file}</a> - <tt>{size}</tt>\n")
    print(reply)

getContent("s25")