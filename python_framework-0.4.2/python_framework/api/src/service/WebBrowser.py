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
    parsedUrl = getParsedUrl(url)
    if anonymous :
        try :
            webbrowser.get(f'{getBrowserPath("chrome")}{" --incognito"}').open_new_tab(parsedUrl)
        except Exception as exception:
            log.warning(openUrlInChrome, 'Failed to open browser in incognition mode', exception=exception)
            return webbrowser.get(getBrowserPath('chrome')).open_new_tab(parsedUrl)
    else:
        return webbrowser.get(getBrowserPath('chrome')).open_new_tab(parsedUrl)

def openUrl(url) :
    parsedUrl = getParsedUrl(url)
    webbrowser.open_new(parsedUrl)

def getParsedUrl(url, host='localhost') :
    urlAsString = str(url)
    if '0.0.0.0' in urlAsString :
        urlAsString = urlAsString.replace('0.0.0.0', host)
    return urlAsString
