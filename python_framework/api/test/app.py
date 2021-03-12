import globals
globalsInstance = globals.newGlobalsInstance(__file__
    , settingStatus = True
    , successStatus = True
    , errorStatus = True
    , debugStatus = True
    , failureStatus = True
    # , warningStatus = True
    # , wrapperStatus = True
    # , logStatus = True
)

from python_framework import initialize
import TestApi
app = TestApi.app
api = TestApi.api
jwt = TestApi.jwt

@initialize(api, defaultUrl = '/swagger', openInBrowser=False)
def runFlaskApplication(app):
    app.run(debug=True,use_reloader=False)
    # app.run(debug=True)

if __name__ == '__main__' :
    runFlaskApplication(app)
