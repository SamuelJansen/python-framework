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
    # , wrapperStatus = True
    # , logStatus = True
    # , testStatus = True
)

from python_framework.api.src.service.flask.FlaskManager import initialize
import TestApi
app = TestApi.app
api = TestApi.api
jwt = TestApi.jwt

@initialize(api, defaultUrl = '/swagger', openInBrowser=False)
def runFlaskApplication(app):
    app.run(debug=False, use_reloader=False)
    # app.run(debug=True)

if __name__ == '__main__' :
    runFlaskApplication(app)
