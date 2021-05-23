import webbrowser
import platform

def getBrowserPath(browserName) :
    if browserName == 'chrome' and platform.system() == 'Windows':
         return 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    elif browserName == 'chrome' and platform.system() == 'Linux':
        return '/usr/bin/google-chrome %s'
    elif browserName == 'chrome' and platform.system() == 'Darwin' or platform.system() == 'Java':
        return 'open -a /Applications/Google\ Chrome.app %s'
    elif browserName == 'opera' and platform.system() == 'Windows':
        return 'C:/Users/'+ os.getlogin() +'/AppData/Local/Programs/Opera/launcher.exe'
    elif browserName == 'iexplore' and platform.system() == 'Windows':
        return 'C:/Program Files/internet explorer/iexplore.exe %s'
    elif browserName == 'firefox' and platform.system() == 'Windows':
        return 'C:/Program Files/Mozilla Firefox/firefox.exe'
    else:
        return ''

def openUrlInChrome(url, anonymous=False) :
    parsedUrl = getParsedUrl(getParsedUrl)
    # webbrowser.open_new(parsedUrl)
    if anonymous :
        try :
            webbrowser.get(f'{getBrowserPath("chrome")}{" --incognito"}').open_new_tab(parsedUrl)
        except :
            webbrowser.get(getBrowserPath('chrome')).open_new_tab(parsedUrl)
    return webbrowser.get(getBrowserPath('chrome')).open_new_tab(parsedUrl)

def openUrl(url) :
    parsedUrl = getParsedUrl(getParsedUrl)
    webbrowser.open_new(parsedUrl)

def getParsedUrl(url, host='localhost') :
    return str(url).replace('0.0.0.0', host)

# import time
# import subprocess
# import os
# import sys

# privateServerLink = 'https://www.roblox.com/games/2414851778/TIER-20-Dungeon-Quest?privateServerLinkCode=GXVlmYh0Z7gwLPBf7H5FWk3ClTVesorY'

# browserName = input(str("Browser Type: chrome, opera, iexplore, firefox : "))
# userSleepTime = int(input("How long do you want it to run?"))
# if browserName == 'opera':
#     userBrowserD = 'launcher.exe'
# else:
#     userBrowserD = browserName
#
# if browserName == "chrome":
#     taskToKill = "chrome.exe"
# else:
#     taskToKill = "iexplore.exe"


# while 1 == 1:
#     subprocess.Popen('SynapseX.exe')
#     time.sleep(7)
#     webbrowser.get(browserPath).open_new_tab(privateServerLink)
#     time.sleep(7)
#     os.system('taskkill /f /im '+taskToKill)
#     time.sleep(userSleepTime)
