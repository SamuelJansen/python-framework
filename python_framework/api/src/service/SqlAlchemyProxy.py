import os
from python_helper import Constant as c
from python_helper import SettingHelper, EnvironmentHelper, ObjectHelper, StringHelper
import sqlalchemy
from sqlalchemy import create_engine, exists, select
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, UnicodeText, MetaData, Sequence, DateTime, Date, Time, Interval, Boolean
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import literal

from python_helper import log, Method, Function

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

@Function
def getNewModel() :
    return declarative_base()

@Function
def attributeIt(modelName) :
    return f'{modelName[0].lower()}{modelName[1:]}'

@Function
def getManyToMany(sister, brother, refferenceModel) :
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
def getOneToMany(owner, pet, refferenceModel) :
    return relationship(pet, back_populates=attributeIt(f'{owner}'), cascade=CASCADE_ONE_TO_MANY)

@Function
def getManyToOne(pet, owner, refferenceModel) :
    ownerId = Column(Integer(), ForeignKey(f'{owner}{c.DOT}{attributeIt(ID)}'))
    owner = relationship(owner, back_populates=attributeIt(f'{pet}{LIST}'))
    return owner, ownerId

@Function
def getOneToOneParent(parent, child, refferenceModel) :
    childAttribute = relationship(child, uselist=False, back_populates=attributeIt(parent))
    return childAttribute

@Function
def getOneToOneChild(child, parent, refferenceModel) :
    parentId = Column(Integer(), ForeignKey(f'{parent}{c.DOT}{attributeIt(ID)}'))
    parentAttribute = relationship(parent, back_populates=attributeIt(child))
    return parentAttribute, parentId

def isNeitherNoneNorBlank(thing) :
    return ObjectHelper.isNotNone(thing) and StringHelper.isNotBlank(thing)

def isNoneOrBlank(thing) :
    return ObjectHelper.isNone(thing) or StringHelper.isBlank(thing)

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
        self.model = model
        self.model.metadata.bind = self.engine
        # self.model.metadata.reflect()

        self.run()

    def getNewEngine(self, dialect, echo, connectArgs) :
        # MODEL = MODEL = getNewModel()
        # schemaFromEnvironment = EnvironmentHelper.get(SqlAlchemyProxy.ENV_DATABASE_SCHEMA)
        # schemaProperty = globalsInstance.getSetting(f'{SqlAlchemyProxy.KW_API}{c.DOT}{SqlAlchemyProxy.KW_DATABASE}{c.DOT}{SqlAlchemyProxy.KW_REPOSITORY_SCHEMA}')
        # if ObjectHelper.isNotNone(schemaFromEnvironment) :
        #     MODEL.metadata.schema = schemaFromEnvironment
        # elif ObjectHelper.isNotNone(schemaProperty) :
        #     MODEL.metadata.schema = schemaProperty
        url = self.getUrl(dialect)
        connectArgs = self.getConnectArgs(connectArgs)
        engine = None
        try :
            engine = create_engine(url, echo=echo, connect_args=connectArgs)
        except Exception as exception :
            log.error(self.getNewEngine, 'Not possible to parse database url environment variable', exception)
            # log.prettyPython(self.getNewEngine, 'settingsFileName', self.globals.settingsFileName, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'settingFilePath', self.globals.settingFilePath, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'settingTree', self.globals.settingTree, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'defaultSettingFileName', self.globals.defaultSettingFileName, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'defaultSettingFilePath', self.globals.defaultSettingFilePath, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'defaultSettingTree', self.globals.defaultSettingTree, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'url', url, logLevel=log.LOG)
            # log.prettyPython(self.getNewEngine, 'connectArgs', connectArgs, logLevel=log.LOG)
            raise exception
        return engine

    def getUrl(self, dialect) :
        log.log(self.getUrl, 'Loading repository configuration')
        url = EnvironmentHelper.get(self.ENV_DATABASE_URL)
        if isNeitherNoneNorBlank(url) :
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
            if isNeitherNoneNorBlank(url) :
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
                if isNeitherNoneNorBlank(username) and isNeitherNoneNorBlank(password) :
                    url += f'{username}{c.COLON}{password}'
                if isNeitherNoneNorBlank(host) and isNeitherNoneNorBlank(port) :
                    url += f'{c.ARROBA}{host}{c.COLON}{port}'
                url += c.SLASH
                database = f'{database}' if isNeitherNoneNorBlank(database) else f'{self.DEFAULT_LOCAL_STORAGE_NAME if ObjectHelper.isNone(self.globals.apiName) else self.globals.apiName}{c.DOT}{self.EXTENSION}'
                if not isNeitherNoneNorBlank(dialect) :
                    dialect = self.DEFAULT_DIALECT
                plusDriverOrNothing = f'{c.PLUS}{driver}' if isNeitherNoneNorBlank(driver) else c.NOTHING
                dialectAndDriver = f'''{dialect}{plusDriverOrNothing}'''
                url = f'{dialectAndDriver}{c.COLON}{c.DOUBLE_SLASH}{url}{database}'
                log.log(self.getUrl, 'Prioritising repository yamel configuration')
        if SettingHelper.activeEnvironmentIsLocal() :
            log.prettyPython(self.getUrl, 'Repository configuations', {**self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}'), **{
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

    def getConnectArgs(self, connectArgs) :
        if ObjectHelper.isNone(connectArgs) :
            connectArgs = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_SETTINGS}')
            connectArgs = {} if ObjectHelper.isNotDictionary(connectArgs) else connectArgs
        # log.prettyPython(self.getConnectArgs, 'connectArgs', connectArgs, logLevel=log.LOG)
        return connectArgs

    @Method
    def run(self):
        try :
            self.model.metadata.create_all(self.engine)
        except Exception as exception :
            log.error(self.run, 'Not possible to run', exception)
            # log.prettyPython(self.run, 'settingsFileName', self.globals.settingsFileName, logLevel=log.LOG)
            # log.prettyPython(self.run, 'settingFilePath', self.globals.settingFilePath, logLevel=log.LOG)
            # log.prettyPython(self.run, 'settingTree', self.globals.settingTree, logLevel=log.LOG)
            # log.prettyPython(self.run, 'defaultSettingFileName', self.globals.defaultSettingFileName, logLevel=log.LOG)
            # log.prettyPython(self.run, 'defaultSettingFilePath', self.globals.defaultSettingFilePath, logLevel=log.LOG)
            # log.prettyPython(self.run, 'defaultSettingTree', self.globals.defaultSettingTree, logLevel=log.LOG)
            # url = self.getUrl(self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_DIALECT}'))
            # connectArgs = self.getConnectArgs(None)
            # log.prettyPython(self.run, 'url', url, logLevel=log.LOG)
            # log.prettyPython(self.run, 'connectArgs', connectArgs, logLevel=log.LOG)

    @Method
    def commit(self):
        self.session.commit()

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
    def existsByQueryAndCommit(self, query, modelClass) :
        exists = self.session.query(literal(True)).filter(self.session.query(modelClass).filter_by(**query).exists()).scalar()
        self.session.commit()
        return exists

    @Method
    def findAllByQueryAndCommit(self, query, modelClass):
        objectList = []
        if query :
            objectList = self.session.query(modelClass).filter_by(**query).all()
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
