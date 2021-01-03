from globals import Globals
globals = Globals(__file__,
    successStatus = True,
    settingStatus = True,
    debugStatus = True,
    warningStatus = True,
    failureStatus = True,
    errorStatus = True
    , logStatus = True
)
import TestApi
app = TestApi.app
api = TestApi.api
jwt = TestApi.jwt

if __name__ == '__main__' :
    app.run(debug=True)
