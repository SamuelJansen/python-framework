from python_helper import Constant as c
from python_helper import EnvironmentHelper
from flask_apscheduler import APScheduler

def addScheduler(api, app) :
    # initialize scheduler
    scheduler = APScheduler()
    # if you don't wanna use a config, you can set options here:
    scheduler.api_enabled = api.globals.getApiSetting('api.scheduler.enable') is True or c.TRUE == api.globals.getApiSetting('api.scheduler.enable')
    api.scheduler = scheduler
    return scheduler

def initialize(api, app) :
    api.scheduler.init_app(app)
    api.scheduler.start()

def shutdown(api, app) :
    import atexit
    atexit.register(lambda: api.scheduler.shutdown(wait=False))
