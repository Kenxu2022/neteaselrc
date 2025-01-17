import json
import os, sys
import re
from prettytable import PrettyTable
from argparse import ArgumentParser
from configparser import ConfigParser
from lyrics import parseLyrics
from api import searchMusic, searchAlbum, getAlbumInfo

# get config directory
scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.conf")

config = ConfigParser()
config.read(configPath)

omitListStr = config['General']['OMIT_LIST']
extListStr = config['General']['EXTENSION_LIST']
OMIT_LIST = [keyword.strip() for keyword in omitListStr.split(',') if keyword.strip()]
EXTENSION_LIST = [keyword.strip() for keyword in extListStr.split(',')]

if (not OMIT_LIST):
    print("未设置忽略关键词名单，将跳过匹配")

def getFile(dir):
    fileName = []
    for file in os.listdir(dir):
        if (os.path.isfile(f"{dir}/{file}")):
            extension = os.path.splitext(file)[1]
            if extension in EXTENSION_LIST:
                fileName.append(os.path.splitext(file)[0])
    return sorted(fileName)

def ifLyricsExist(dir, name):
    lrcExist = False
    for file in os.listdir(dir):
        if (os.path.isfile(f"{dir}/{file}")):
            extension = os.path.splitext(file)[1]
            if extension == '.lrc':
                if os.path.splitext(file)[0] == name:
                    lrcExist = True
                    break
    return lrcExist

# parse argument
parser = ArgumentParser(prog='neteaselrc', description='Download lyrics from Netease Cloud Music')
parser.add_argument('-d', '--directory', required=False, help='specify directory')
parser.add_argument('-al', '--album', required=False, help='specify album for better accuracy')
parser.add_argument('-ar', '--artist', required=False, help='specify artist for better accuracy')
args = parser.parse_args()
dir = args.directory
album = args.album
artist = args.artist

if (dir is None):
    dir = os.path.abspath('.')

print(f"搜索路径: {dir}")

musicList = getFile(dir)
print(f"获取到的歌曲列表: {musicList}")
if (not musicList):
    print("没有获取到歌曲，请检查文件夹中的内容或config.conf中扩展名项的配置是否正确")
    sys.exit()

searchType = int(input("请选择搜索方式，1为按歌曲搜索，2为按专辑搜索："))
if (searchType == 1):
    for music in musicList:
        extraInfo = [album, artist]
        # parse search name using regexp
        searchName = re.sub(r'^\d+\s*[.\-_]*\s*', '', music).strip()
        # parse arguments
        for args in extraInfo:
            if (args is not None):
                searchName = searchName + ' ' + args
        print(f"搜索名称: {searchName}")

        # omit if file name contain certain keywords
        print(music.lower())
        print(OMIT_LIST)
        if (any(keyword in music.lower() for keyword in OMIT_LIST)):
            choice = input("检测到特定关键词，该文件可能为纯音乐，ENTER可跳过：")
            if (choice == ''):
                continue

        # omit if lrc file already exists    
        lrcStatus = ifLyricsExist(dir, music)
        if (lrcStatus == True):
            choice = input("歌词文件已存在，ENTER可跳过：")
            if (choice == ''):
                continue

        searchResult = searchMusic(searchName)
        # print(f"Search result: {searchResult}")
        searchData = json.loads(searchResult)
        if ("result" in searchData and "songs" in searchData["result"]):
            searchTable = PrettyTable()
            searchTable.field_names = ["序号", "ID", "歌曲名称", "作曲家", "专辑"]
            for r in range(len(searchData["result"]["songs"])):
                songId = searchData["result"]["songs"][r]["id"]
                songName = searchData["result"]["songs"][r]["name"]
                songArtist = searchData["result"]["songs"][r]["ar"][0]["name"]
                songAlbum = searchData["result"]["songs"][r]["al"]["name"]

                searchTable.add_row([r + 1, songId, songName, songArtist, songAlbum])

            print(searchTable)
        else:
            print("未找到歌曲！")
            continue

        searchChoice = input("输入歌曲序号，ENTER可以跳过：")

        # search for lyrics according to setected songId
        if (searchChoice == ''):
            continue
        else:
            searchChoice = int(searchChoice)
            songId = searchData["result"]["songs"][searchChoice - 1]["id"]

        result = parseLyrics(songId, dir, music)
        if (result == 1):
                    print(f"歌词为空，可能是纯音乐或未上传歌词：{music}")
        elif (result == 2):
            print(f"歌曲为纯音乐，跳过该曲：{music}")
        else:
            print(f"成功将歌曲: {music} 对应歌词写入文件!")

elif (searchType == 2):
    if (album is None):
        album = os.path.basename(os.getcwd())

    if (artist is not None):
        searchName = album + ' ' + artist
    else:
        searchName = album

    print(f"搜索名称: {searchName}")
    searchAlbumResult = searchAlbum(searchName)
    # print(searchAlbumResult)

    searchAlbumData = json.loads(searchAlbumResult)
    if ("result" in searchAlbumData and "albums" in searchAlbumData["result"]):
        searchAlbumTable = PrettyTable()
        searchAlbumTable.field_names = ["序号", "ID", "专辑名称", "作曲家", "曲目数量"]
        for r in range(len(searchAlbumData["result"]["albums"])):
            albumId = searchAlbumData["result"]["albums"][r]["id"]
            albumName = searchAlbumData["result"]["albums"][r]["name"]
            albumArtist = searchAlbumData["result"]["albums"][r]["artist"]["name"]
            albumSongCount = searchAlbumData["result"]["albums"][r]["size"]

            searchAlbumTable.add_row([r + 1, albumId, albumName, albumArtist, albumSongCount])
        
        print(searchAlbumTable)
    else:
        print("未找到专辑！")
        sys.exit()

    searchChoice = int(input("输入专辑序号："))
    albumId = searchAlbumData["result"]["albums"][searchChoice - 1]["id"]

    # print(getAlbumInfo(albumId))
    songInfo = json.loads(getAlbumInfo(albumId))
    songTable = PrettyTable()
    if (len(songInfo["songs"]) == len(musicList)):
        songTable.field_names = ["序号", "文件夹内歌曲名称", "专辑内歌曲名称"]
        for r in range(len(songInfo["songs"])):
            songNameFromFolder = musicList[r]
            songNameFromAlbum = songInfo["songs"][r]["name"]
            songTable.add_row([r + 1, songNameFromFolder, songNameFromAlbum])

        print("歌曲数量相符，请根据表格确认名称是否正确：")
        print(songTable)
        confirm = input("确认请直接按ENTER，其他按键可以取消：")
        if confirm == '':
            for r in range(len(songInfo["songs"])):                
                songId = songInfo["songs"][r]["id"]
                music = musicList[r]
                
                # omit if file name contain certain keywords
                if (any(keyword in music.lower() for keyword in OMIT_LIST)):
                    choice = input("检测到特定关键词，该文件可能为纯音乐，ENTER可跳过：")
                    if (choice == ''):
                        continue

                # omit if lrc file already exists    
                lrcStatus = ifLyricsExist(dir, music)
                if (lrcStatus == True):
                    choice = input("歌词文件已存在，ENTER可跳过：")
                    if (choice == ''):
                        continue
                
                result = parseLyrics(songId, dir, music)
                if (result == 1):
                    print(f"歌词为空，可能是纯音乐或未上传歌词：{music}")
                elif (result == 2):
                    print(f"歌曲为纯音乐，跳过该曲：{music}")
                else:
                    print(f"成功将歌曲: {music} 对应歌词写入文件!")

    else:
        print("文件夹内歌曲数量与专辑内歌曲数量不相符，请改用按歌曲搜索！")
        print("以下是专辑内歌曲信息：")
        songTable.field_names = ["序号", "专辑内歌曲名称"]
        for r in range(len(songInfo["songs"])):
            songNameFromAlbum = songInfo["songs"][r]["name"]
            songTable.add_row([r + 1, songNameFromAlbum])
        print(songTable)
else:
    print("输入无效！")