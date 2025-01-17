import requests
import os, sys
from configparser import ConfigParser

scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.conf")

config = ConfigParser()
config.read(configPath)

BASE_URL = config['General']['BASE_URL']
if (not BASE_URL):
    print("NeteaseCloudMusicApi实例地址为空，请检查配置！")
    sys.exit()

def searchMusic(name):
    url = f"{BASE_URL}/cloudsearch"
    parameter = {
        "keywords": name,
        "limit": 5,
        "type": 1
    }
    response = requests.get(url=url, params=parameter)
    return response.text

def searchLyric(id):
    url = f"{BASE_URL}/lyric"
    parameter = {
        "id": id
    }
    response = requests.get(url=url, params=parameter)
    return response.text

def searchAlbum(name):
    url = f"{BASE_URL}/cloudsearch"
    parameter = {
        "keywords": name,
        "limit": 5,
        "type": 10
    }
    response = requests.get(url=url, params=parameter)
    return response.text

def getAlbumInfo(id):
    url = f"{BASE_URL}/album"
    parameter = {
        "id": id
    }
    response = requests.get(url=url, params=parameter)
    return response.text