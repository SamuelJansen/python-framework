import os, time

from python_helper import Constant as c
from python_helper import SettingHelper, EnvironmentHelper, ObjectHelper, StringHelper, log, Method, Function

import sqlalchemy
from sqlalchemy import create_engine, exists, select
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, close_all_sessions
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, UnicodeText, MetaData, Sequence, DateTime, Date, Time, Interval, Boolean
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import literal

and_ = and_
or_ = or_

UnicodeText = UnicodeText
DateTime = DateTime
Date = Date
Time = Time
Interval = Interval

Table = Table
Column = Column

Integer = Integer
String = String
Float = Float
Boolean = Boolean

exists = exists
select = select
literal = literal

relationship = relationship

Sequence = Sequence
ForeignKey = ForeignKey
MetaData = MetaData

DeclarativeMeta = DeclarativeMeta

InstrumentedList = InstrumentedList

MANY_TO_MANY = '''And'''
ID = '''Id'''
SEQ = '''Seq'''
LIST = '''List'''

CASCADE_ONE_TO_MANY = '''all,delete'''


GIANT_STRING_SIZE = 16384
LARGE_STRING_SIZE = 1024
STRING_SIZE = 512
MEDIUM_STRING_SIZE = 128
LITTLE_STRING_SIZE = 64


MODEL_PATTERN_NAME = 'Model'

###- https://docs.sqlalchemy.org/en/14/orm/events.html#instance-events
from sqlalchemy import event

class OnORMChangeEventType:
    UNKNOWN = 'UNKNOWN'
    LOAD = 'LOAD'
    REFRESH = 'REFRESH'

def onLoadListener(target, context):
    target.onLoad(context)

def onRefreshListener(target, context, attributes):
    target.onRefresh(context, attributes)

def getNewOriginalModel():
    return declarative_base()

class PythonFramworkBaseClass(getNewOriginalModel()):
    __abstract__ = True
    def onChange(self, eventType, *args, **kwargs):
        ...
    def onLoad(self, context):
        self.onChange(OnORMChangeEventType.LOAD, context)
    def onRefresh(self, context, attributes):
        self.onChange(OnORMChangeEventType.REFRESH, context, attributes)

@Function
def getNewModel():
    # ORIGINAL_BASE_MODEL = getNewOriginalModel()
    # class PythonFramworkBaseClass(ORIGINAL_BASE_MODEL):
    #     def onChange(self, eventType, *args, **kwargs):
    #         ...
    #     def onLoad(self, target, context):
    #         self.onChange(OnORMChangeEventType.LOAD, target, context)
    #     def onRefresh(self, target, context, attributes):
    #         self.onChange(OnORMChangeEventType.REFRESH, target, context, attributes)

    # return declarative_base()
    return declarative_base(cls=PythonFramworkBaseClass, name='PythonFramworkBaseClass')

@Function
def attributeIt(modelName):
    return f'{modelName[0].lower()}{modelName[1:]}'.replace(MODEL_PATTERN_NAME, c.BLANK)

@Function
def getManyToMany(sister, brother, refferenceModel):
    # featureList = relationship(FEATURE, secondary=featureToSampleAssociation, back_populates=attributeIt(f'{__tablename__}{LIST}'))
    # sampleList = relationship(SAMPLE, secondary=featureToSampleAssociation, back_populates=attributeIt(f'{__tablename__}{LIST}'))
    manySisterToManyBrother = Table(
        f'{sister}{MANY_TO_MANY}{brother}', refferenceModel.metadata,
        Column(f'{attributeIt(sister)}{ID}', Integer(), ForeignKey(f'{sister}{c.DOT}{attributeIt(ID)}'), primary_key=True),
        Column(f'{attributeIt(brother)}{ID}', Integer(), ForeignKey(f'{brother}{c.DOT}{attributeIt(ID)}'), primary_key=True)
    )
    sisterList = relationship(sister, secondary=manySisterToManyBrother, back_populates=attributeIt(f'{brother}{LIST}'))
    brotherList = relationship(brother, secondary=manySisterToManyBrother, back_populates=attributeIt(f'{sister}{LIST}'))
    ### sister recieves the brotherList
    ### brother recieves the sisterList
    return sisterList, brotherList, manySisterToManyBrother

@Function
def getOneToMany(owner, pet, refferenceModel):
    ###- please try and add "single_parent=True"
    ###- return relationship(pet, back_populates=attributeIt(f'{owner}'), single_parent=True, cascade=CASCADE_ONE_TO_MANY)
    return relationship(pet, back_populates=attributeIt(f'{owner}'), cascade=CASCADE_ONE_TO_MANY)

@Function
def getManyToOne(pet, owner, refferenceModel):
    ownerId = Column(Integer(), ForeignKey(f'{owner}{c.DOT}{attributeIt(ID)}'))
    owner = relationship(owner, back_populates=attributeIt(f'{pet}{LIST}'))
    return owner, ownerId

@Function
def getOneToOneParent(parent, child, refferenceModel):
    childAttribute = relationship(child, uselist=False, back_populates=attributeIt(parent))
    return childAttribute

@Function
def getOneToOneChild(child, parent, refferenceModel):
    parentId = Column(Integer(), ForeignKey(f'{parent}{c.DOT}{attributeIt(ID)}'))
    parentAttribute = relationship(parent, back_populates=attributeIt(child))
    return parentAttribute, parentId

def isNeitherNoneNorBlank(thing):
    return ObjectHelper.isNotNone(thing) and StringHelper.isNotBlank(str(thing))

def isNoneOrBlank(thing):
    return ObjectHelper.isNone(thing) or StringHelper.isBlank(str(thing))


class SqlAlchemyProxy:

    DEFAULT_DRIVER = 'psycopg2'

    KW_API = 'api'
    KW_MAIN_URL = 'main-url'

    KW_URL = 'url'
    KW_DATABASE = 'database'

    KW_REPOSITORY_DIALECT = 'dialect'
    KW_REPOSITORY_DRIVER = 'driver'
    KW_REPOSITORY_DATABASE = 'database'
    KW_REPOSITORY_USERNAME = 'username'
    KW_REPOSITORY_PASSWORD = 'password'
    KW_REPOSITORY_HOST = 'host'
    KW_REPOSITORY_PORT = 'port'
    KW_REPOSITORY_SCHEMA = 'schema'
    KW_REPOSITORY_URL = 'url'
    KW_REPOSITORY_SETTINGS = 'settings'

    ENV_DATABASE_NAME = 'DATABASE_NAME'
    ENV_REPOSITORY_DRIVER = 'DATABASE_DRIVER'
    ENV_DATABASE_DIALECT = 'DATABASE_DIALECT'
    ENV_DATABASE_USERNAME = 'DATABASE_USERNAME'
    ENV_DATABASE_PASSWORD = 'DATABASE_PASSWORD'
    ENV_DATABASE_HOST = 'DATABASE_HOST'
    ENV_DATABASE_PORT = 'DATABASE_PORT'
    ENV_DATABASE_SCHEMA = 'DATABASE_SCHEMA'
    ENV_DATABASE_URL = 'DATABASE_URL'

    DEFAULT_LOCAL_STORAGE_NAME = 'LocalStorage'
    DEFAULT_DIALECT = 'sqlite'
    EXTENSION = 'db'

    def __init__(self,
            model,
            globals,
            echo = False,
            connectArgs = None
        ):
        self.globals = globals
        self.sqlalchemy = sqlalchemy
        dialect = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_DIALECT}')
        self.engine = self.getNewEngine(dialect, echo, connectArgs)
        self.session = scoped_session(sessionmaker(self.engine)) ###- sessionmaker(bind=self.engine)()
        # self.session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine)) ###- sessionmaker(bind=self.engine)()
        self.model = model
        self.model.metadata.bind = self.engine
        # self.model.metadata.reflect()
        # self.run()
        event.listen(PythonFramworkBaseClass, 'load', onLoadListener, propagate=True, restore_load_context=True)
        event.listen(PythonFramworkBaseClass, 'refresh', onRefreshListener, restore_load_context=True)
        log.debug(self.__init__, 'Database initialized')

    def getNewEngine(self, dialect, echo, connectArgs):
        url = self.getUrl(dialect)
        connectArgs = self.getConnectArgs(connectArgs)
        engine = None
        try :
            engine = create_engine(url, echo=echo, connect_args=connectArgs)
        except Exception as exception :
            log.error(self.getNewEngine, 'Not possible to create engine', exception)
            raise exception
        return engine

    def close(self):
        try:
            close_all_sessions()
            self.engine.dispose() # NOTE: close required before dispose!
        except Exception as firstException:
            log.warning(self.close, 'Not possible to close connections. Going for a second attempt', exception=firstException)
            try:
                close_all_sessions()
                self.engine.dispose() # NOTE: close required before dispose!
            except Exception as secondException:
                log.error(self.close, 'Not possible to close connections at the second attempt either', secondException)
                raise secondException
        log.debug(self.close, 'Connections closed')

    def getUrl(self, dialect):
        log.log(self.getUrl, 'Loading repository configuration')
        url = EnvironmentHelper.get(self.ENV_DATABASE_URL)
        if isNeitherNoneNorBlank(url):
            dialect = None
            driver = None
            database = None
            username = None
            password = None
            host = None
            port = None
            schema = None
            log.log(self.getUrl, f'Prioritising repository url in {self.ENV_DATABASE_URL} environment variable')
        else :
            url = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_URL}')
            if isNeitherNoneNorBlank(url):
                dialect = None
                driver = None
                database = None
                username = None
                password = None
                host = None
                port = None
                schema = None
                log.log(self.getUrl, f'Prioritising repository url in yamel configuration')
            else :
                url = c.NOTHING
                driver = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_DRIVER}')
                database = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_DATABASE}')
                username = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_USERNAME}')
                password = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_PASSWORD}')
                host = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_HOST}')
                port = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_PORT}')
                schema = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_SCHEMA}')
                if isNeitherNoneNorBlank(username) and isNeitherNoneNorBlank(password):
                    url += f'{username}{c.COLON}{password}'
                if isNeitherNoneNorBlank(host) and isNeitherNoneNorBlank(port):
                    url += f'{c.ARROBA}{host}{c.COLON}{port}'
                url += c.SLASH
                database = f'{database}' if isNeitherNoneNorBlank(database) else f'{self.DEFAULT_LOCAL_STORAGE_NAME if ObjectHelper.isNone(self.globals.apiName) else self.globals.apiName}{c.DOT}{self.EXTENSION}'
                if not isNeitherNoneNorBlank(dialect):
                    dialect = self.DEFAULT_DIALECT
                plusDriverOrNothing = f'{c.PLUS}{driver}' if isNeitherNoneNorBlank(driver) else c.NOTHING
                dialectAndDriver = f'''{dialect}{plusDriverOrNothing}'''
                url = f'{dialectAndDriver}{c.COLON}{c.DOUBLE_SLASH}{url}{database}'
                log.log(self.getUrl, 'Prioritising repository yamel configuration')
        if SettingHelper.activeEnvironmentIsLocal():
            log.prettyJson(self.getUrl, 'Repository configuations', {**self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}'), **{
                'dialect' : dialect,
                'driver' : driver,
                'database' : database,
                'username' : username,
                'password' : password,
                'host' : host,
                'port' : port,
                'schema' : schema,
                'url' : url
            }}, logLevel = log.SETTING)
        # log.prettyPython(self.getUrl, 'url', url, logLevel=log.LOG)
        return url

    def getConnectArgs(self, connectArgs):
        if ObjectHelper.isNone(connectArgs):
            connectArgs = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_SETTINGS}')
            connectArgs = {} if ObjectHelper.isNotDictionary(connectArgs) else connectArgs
        return connectArgs

    @Method
    def run(self):
        try :
            self.model.metadata.create_all(self.engine)
        except Exception as firstException :
            waittingTime = 30
            log.warning(self.run, f'Not possible to run. Going for a second attemp in {waittingTime} seconds', exception=firstException)
            time.sleep(waittingTime)
            try :
                self.model.metadata.create_all(self.engine)
            except Exception as secondException :
                waittingTime = 30
                log.warning(self.run, f'Not possible to run either. Going for a third and last attemp in {waittingTime} seconds', exception=secondException)
                time.sleep(waittingTime)
                try :
                    self.model.metadata.create_all(self.engine)
                except Exception as thirdException :
                    log.error(self.run, 'Not possible to run', thirdException)
                    raise thirdException
        log.debug(self.run, 'Database tables created')

    @Method
    def flush(self):
        self.session.flush()

    @Method
    def rollback(self):
        self.session.rollback()

    @Method
    def commit(self):
        self.session.commit()

    def onChange(self, modelLoad):
        if ObjectHelper.isNone(modelLoad):
            return modelLoad
        if ObjectHelper.isCollection(modelLoad) or type(modelLoad) == InstrumentedList:
            for model in modelLoad:
                model.onChange()
            return modelLoad
        return modelLoad.onChange()

    @Method
    def save(self, instance):
        self.session.add(instance)

    @Method
    def saveNew(self, *args):
        modelClass = args[-1]
        return self.save(modelClass(*args[:-1]))

    @Method
    def saveAndCommit(self, instance):
        self.save(instance)
        self.session.commit()
        return instance

    @Method
    def saveNewAndCommit(self, *args):
        modelClass = args[-1]
        return self.saveAndCommit(modelClass(*args[:-1]))

    @Method
    def saveAll(self, instanceList):
        self.session.add_all(instanceList)
        return instanceList

    @Method
    def saveAllAndCommit(self, instanceList):
        self.saveAll(instanceList)
        self.session.commit()
        return instanceList

    @Method
    def findAll(self, modelClass):
        objectList = self.session.query(modelClass).all()
        return objectList

    @Method
    def findAllAndCommit(self, modelClass):
        objectList = self.findAll(modelClass)
        self.session.commit()
        return objectList

    @Method
    def findByIdAndCommit(self, id, modelClass):
        object = self.session.query(modelClass).filter(modelClass.id == id).first()
        self.session.commit()
        return object

    @Method
    def existsByIdAndCommit(self, id, modelClass):
        # ret = Session.query(exists().where(and_(Someobject.field1 == value1, Someobject.field2 == value2)))
        objectExists = self.session.query(exists().where(modelClass.id == id)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByKeyAndCommit(self, key, modelClass):
        object = self.session.query(modelClass).filter(modelClass.key == key).first()
        self.session.commit()
        return object

    @Method
    def existsByKeyAndCommit(self, key, modelClass):
        objectExists = self.session.query(exists().where(modelClass.key == key)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByStatusAndCommit(self,status,modelClass):
        object = self.session.query(modelClass).filter(modelClass.status == status).first()
        self.session.commit()
        return object

    @Method
    def existsByQueryAndCommit(self, query, modelClass):
        exists = self.session.query(literal(True)).filter(self.session.query(modelClass).filter_by(**query).exists()).scalar()
        self.session.commit()
        return exists

    @Method
    def findAllByQueryAndCommit(self, query, modelClass):
        if ObjectHelper.isNotNone(query):
            objectList = self.session.query(modelClass).filter_by(**{k: v for k, v in query.items() if ObjectHelper.isNotNone(v)}).all()
        self.session.commit()
        return objectList

    @Method
    def deleteByIdAndCommit(self, id, modelClass):
        if self.session.query(exists().where(modelClass.id == id)).one()[0] :
            object = self.session.query(modelClass).filter(modelClass.id == id).first()
            self.session.delete(object)
        self.session.commit()

    @Method
    def deleteByKeyAndCommit(self, key, modelClass):
        if self.session.query(exists().where(modelClass.key == key)).one()[0] :
            object = self.session.query(modelClass).filter(modelClass.key == key).first()
            self.session.delete(object)
        self.session.commit()

    @Method
    def deleteAndCommit(self, object):
        self.session.delete(object)
        self.session.commit()

    @Method
    def deleteAllByIdIn(self, modelClass, objectIdList):
        self.session.query(modelClass).filter(modelClass.id.in_(objectIdList)).delete(synchronize_session=False)

    @Method
    def deleteAllByKeyIn(self, modelClass, objectKeyList):
        self.session.query(modelClass).filter(modelClass.key.in_(objectKeyList)).delete(synchronize_session=False)

    @Method
    def deleteAllByIdInAndCommit(self, modelClass, objectIdList):
        self.deleteAllByIdIn(modelClass, objectIdList)
        self.session.commit()

    @Method
    def deleteAllByKeyInAndCommit(self, modelClass, objectKeyList):
        self.deleteAllByKeyIn(modelClass, objectKeyList)
        self.session.commit()


def addResource(apiInstance, appInstance, baseModel=None, echo=False):
    apiInstance.repository = SqlAlchemyProxy(baseModel, apiInstance.globals, echo=echo)
    if ObjectHelper.isNotNone(apiInstance.repository):
        log.status(addResource, 'SqlAlchemyProxy database connection created')
    return apiInstance.repository

def initialize(apiInstance, appInstance):
    apiInstance.repository.run()
    log.success(initialize, 'SqlAlchemyProxy database is running')

def onHttpRequestCompletion(apiInstance, appInstance):
    @appInstance.teardown_appcontext
    def closeSqlAlchemyProxySession(error):
        try:
            try:
                apiInstance.repository.session.commit()
            except Exception as innerException:
                log.log(closeSqlAlchemyProxySession, 'Not possible to close SqlAlchemyProxy session', exception=innerException)
            apiInstance.repository.session.close()
        except Exception as exception:
            log.failure(closeSqlAlchemyProxySession, 'Not possible to close SqlAlchemyProxy session', exception)

def shutdown(apiInstance, appInstance):
    try:
        apiInstance.repository.close()
    except Exception as exception:
        log.failure(shutdown, 'Not possible to close SqlAlchemyProxy database connection properly', exception)
        return
    log.success(shutdown, 'SqlAlchemyProxy database connection successfully closed')

def onShutdown(apiInstance, appInstance):
    import atexit
    atexit.register(lambda: shutdown(apiInstance, appInstance))
