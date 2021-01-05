from python_helper import log, ObjectHelper

global GLOBALS
GLOBALS = None

def updateGlobals(globalsInstance) :
    global GLOBALS
    if ObjectHelper.isNone(GLOBALS) :
        GLOBALS = globalsInstance
        log.debug(updateGlobals, f'Setting {globalsInstance} globals instance')
    log.debug(updateGlobals, f'Returning {globalsInstance} globals instance')
    return GLOBALS

def getGlobals() :
    global GLOBALS
    if ObjectHelper.isNotNone(GLOBALS) :
        return GLOBALS
