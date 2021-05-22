from python_helper import EnvironmentHelper, log

from python_helper import SettingHelper

import globals
globalsInstance = globals.newGlobalsInstance(__file__
    , loadLocalConfig = SettingHelper.activeEnvironmentIsDefault()

    , settingStatus = True
    , successStatus = True
    , errorStatus = True

    , debugStatus = True
    , failureStatus = True
    , warningStatus = True
    , wrapperStatus = True
    , logStatus = True
    # , testStatus = True
)

from python_framework.api.src.service.flask import FlaskManager
import TestApi
app = TestApi.app
api = TestApi.api
jwt = TestApi.jwt

@FlaskManager.initialize(api, defaultUrl = '/swagger', openInBrowser=False)
def runFlaskApplication(app=None):
    FlaskManager.runApi(debug=False, use_reloader=False)
    # app.run(debug=False, use_reloader=False)
    # app.run(debug=True)

if __name__ == '__main__' :
    runFlaskApplication()

log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')
