import json
import os

from api import searchLyric

def parseLyrics(lyricId, dir, musicName):
    needTranslation = False
    lyricResult = searchLyric(lyricId)
    # print(lyricResult)
    lyricData = json.loads(lyricResult)
    lyric = lyricData["lrc"]["lyric"]
    if (lyric == ''):
        return 1
    # print(f"{lyric}")
    if "tlyric" in lyricData:
        needTranslation = True
        translatedLyric = lyricData["tlyric"]["lyric"]
        # print(f"{translatedLyric}")
    
    # format timestamp and create dict
    formatLyric = lyric.strip().split('\n')
    # print(formatLyric)
    formatLyricDict = {}
    for line in formatLyric:
        # parse potential invalid format
        if (len(line) >= 10 and line[6] == ':'):
            line = line[:6] + '.' + line[7:]
        lineStart = line.find("[") + 1
        lineEnd = line.find("]")
        # print(f"Timestamp: {line[lineStart:lineEnd]}")
        if (len(line[lineStart:lineEnd]) > 8):
            timestamp = line[:9] + "]"
            content = line[lineEnd + 1:]
        else:
            timestamp = line[:10]
            content = line[10:]

        if (content == "纯音乐，请欣赏"):
            return 2
        formatLyricDict[timestamp] = content
    # print(formatLyricDict)
    
    # parse translated lyrics if needed
    if (needTranslation == True):
        formatTranslatedLyricDict = {}
        formatTranslatedLyric = translatedLyric.strip().split('\n')
        for line in formatTranslatedLyric:
            # parse potential invalid format
            if (len(line) >= 10 and line[6] == ':'):
                line = line[:6] + '.' + line[7:]
            lineStart = line.find("[") + 1
            lineEnd = line.find("]")
            # print(f"Timestamp: {line[lineStart:lineEnd]}")
            if (len(line[lineStart:lineEnd]) > 8):
                timestamp = line[:9] + "]"
                content = line[lineEnd + 1:]
                formatTranslatedLyricDict[timestamp] = content
            else:
                timestamp = line[:10]
                content = line[10:]
                formatTranslatedLyricDict[timestamp] = content
        # print(formatTranslatedLyricDict)
    
    # merge lyrics
    mergedLyrics = []
    for timestamp in formatLyricDict:
        mergedLyrics.append(f"{timestamp}{formatLyricDict[timestamp]}")
        if (needTranslation == True):
            if timestamp in formatTranslatedLyricDict:
                if (formatTranslatedLyricDict[timestamp] == ''):
                    continue
                else:
                    mergedLyrics.append(f"{timestamp}{formatTranslatedLyricDict[timestamp]}")
    # print(mergedLyrics)
    lrcPath = os.path.join(dir, f"{musicName}.lrc")
    with open(lrcPath, 'w') as file:
        for line in mergedLyrics:
            file.write(f"{line}\n")