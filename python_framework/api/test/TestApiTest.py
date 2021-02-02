from python_helper import Test

@Test()
def appRun_withSuccess() :
    import app
    app.runFlaskApplication(app.app)
