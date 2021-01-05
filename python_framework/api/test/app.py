from globals import Globals
globalsInstance = Globals(__file__,
    successStatus = True,
    settingStatus = True,
    debugStatus = True,
    warningStatus = True,
    failureStatus = True,
    errorStatus = True
    , logStatus = True
)

print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')
print('heeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeee')

from python_framework.api.src.service.flask import GlobalsManager
GlobalsManager.GLOBALS = GlobalsManager.updateGlobals(globalsInstance)

from python_framework.api.src.service.flask.FlaskManager import initialize
import TestApi
app = TestApi.app
api = TestApi.api
jwt = TestApi.jwt

@initialize(api, GlobalsManager.GLOBALS, defaultUrl = '/swagger', openInBrowser=False)
def runFlaskApplication(app):
    app.run(debug=True)

if __name__ == '__main__' :
    runFlaskApplication(app)
