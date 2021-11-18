from requests import get


def Sakura(device):
    data = get("https://raw.githubusercontent.com/ProjectSakura/OTA/11/devices.json").json()
    for item in data:
        if item["codename"] == device:
            print(item)
            return
    print("No devices")


Sakura("s2")