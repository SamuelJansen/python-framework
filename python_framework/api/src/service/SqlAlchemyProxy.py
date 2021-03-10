import os
from python_helper import Constant as c
from python_helper import SettingHelper, EnvironmentHelper, ObjectHelper, StringHelper
import sqlalchemy
from sqlalchemy import create_engine, exists, select
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, UnicodeText, MetaData, Sequence, DateTime
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import literal

from python_helper import log, Method, Function

and_ = and_
or_ = or_

UnicodeText = UnicodeText
DateTime = DateTime

Table = Table
Column = Column
Integer = Integer
String = String
Float = Float

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
    manySisterToManyBrother = Table(f'{sister}{MANY_TO_MANY}{brother}', refferenceModel.metadata,
        Column(f'{attributeIt(sister)}{ID}', Integer(), ForeignKey(f'{sister}{c.DOT}{attributeIt(ID)}')),
        Column(f'{attributeIt(brother)}{ID}', Integer(), ForeignKey(f'{brother}{c.DOT}{attributeIt(ID)}')))
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

    KW_API = 'api'
    KW_MAIN_URL = 'main-url'

    KW_URL = 'url'
    KW_DATABASE = 'database'
    KW_REPOSITORY_DIALECT = 'dialect'
    KW_REPOSITORY_USERNAME = 'username'
    KW_REPOSITORY_PASSWORD = 'password'
    KW_REPOSITORY_HOST = 'host'
    KW_REPOSITORY_PORT = 'port'
    KW_REPOSITORY_SCHEMA = 'schema'
    KW_REPOSITORY_URL = 'url'
    KW_REPOSITORY_SETTINGS = 'settings'

    DATABASE_URL_ENIRONMENT_KEY = 'DATABASE_URL'
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

        self.run()

    def getNewEngine(self, dialect, echo, connectArgs) :
        url = self.getUrl(dialect)
        connectArgs = self.getConnectArgs(connectArgs)
        engine = None
        try :
            engine = create_engine(url, echo=echo, connect_args=connectArgs)
        except Exception as exception :
            log.error(self.getNewEngine, 'Not possible to parse database url environment variable', exception)
            raise exception
        return engine

    def getUrl(self, dialect) :
        log.log(self.getUrl, 'Loading repository configuration')
        url = EnvironmentHelper.get(self.DATABASE_URL_ENIRONMENT_KEY)
        if isNeitherNoneNorBlank(url) :
            dialect = None
            username = None
            password = None
            host = None
            port = None
            schema = None
            log.log(self.getUrl, f'Prioritisig repository url in {self.DATABASE_URL_ENIRONMENT_KEY} environment variable')
        else :
            url = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_URL}')
            if isNeitherNoneNorBlank(url) :
                dialect = None
                username = None
                password = None
                host = None
                port = None
                schema = None
                log.log(self.getUrl, f'Prioritisig repository url in yamel configuration')
            else :
                url = c.NOTHING
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
                schema = f'{schema}{c.DOT}{self.EXTENSION}' if isNeitherNoneNorBlank(schema) else f'{self.DEFAULT_LOCAL_STORAGE_NAME if ObjectHelper.isNone(self.globals.apiName) else self.globals.apiName}{c.DOT}{self.EXTENSION}'
                if not isNeitherNoneNorBlank(dialect) :
                    dialect = self.DEFAULT_DIALECT
                url = f'{dialect}{c.COLON}{c.DOUBLE_SLASH}{url}{schema}'
                log.log(self.getUrl, 'Prioritisig repository yamel configuration')
        if SettingHelper.activeEnvironmentIsLocal() :
            log.prettyPython(self.getUrl, 'Repository configuations', {**self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}'), **{
                'dialect' : dialect,
                'username' : username,
                'password' : password,
                'host' : host,
                'port' : port,
                'schema' : schema,
                'url' : url
            }}, logLevel = log.SETTING)
        return url

    def getConnectArgs(self, connectArgs) :
        if ObjectHelper.isNone(connectArgs) :
            connectArgs = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_SETTINGS}')
            finalConnectArgs = {}
            if ObjectHelper.isDictionary(connectArgs) :
                for key, value in connectArgs.items() :
                    finalConnectArgs[key] = value
            return finalConnectArgs
        else :
            return connectArgs

    @Method
    def run(self):
        self.model.metadata.create_all(self.engine)

    @Method
    def commit(self):
        self.session.commit()

    @Method
    def save(self, instance):
        self.session.add(instance)

    @Method
    def saveNew(self, *args):
        model = args[-1]
        return self.save(model(*args[:-1]))

    @Method
    def saveAndCommit(self, instance):
        self.save(instance)
        self.session.commit()
        return instance

    @Method
    def saveNewAndCommit(self, *args):
        model = args[-1]
        return self.saveAndCommit(model(*args[:-1]))

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
    def findAll(self, model):
        objectList = self.session.query(model).all()
        return objectList

    @Method
    def findAllAndCommit(self, model):
        objectList = self.findAll(model)
        self.session.commit()
        return objectList

    @Method
    def findByIdAndCommit(self, id, model):
        object = self.session.query(model).filter(model.id == id).first()
        self.session.commit()
        return object

    @Method
    def existsByIdAndCommit(self, id, model):
        # ret = Session.query(exists().where(and_(Someobject.field1 == value1, Someobject.field2 == value2)))
        objectExists = self.session.query(exists().where(model.id == id)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByKeyAndCommit(self, key, model):
        object = self.session.query(model).filter(model.key == key).first()
        self.session.commit()
        return object

    @Method
    def existsByKeyAndCommit(self, key, model):
        objectExists = self.session.query(exists().where(model.key == key)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByStatusAndCommit(self,status,model):
        object = self.session.query(model).filter(model.status == status).first()
        self.session.commit()
        return object

    @Method
    def existsByQueryAndCommit(self, query, model) :
        exists = self.session.query(literal(True)).filter(self.session.query(model).filter_by(**query).exists()).scalar()
        self.session.commit()
        return exists

    @Method
    def findAllByQueryAndCommit(self, query, model):
        objectList = []
        if query :
            objectList = self.session.query(model).filter_by(**query).all()
        self.session.commit()
        return objectList

    @Method
    def deleteByKeyAndCommit(self, key, model):
        if self.session.query(exists().where(model.key == key)).one()[0] :
            object = self.session.query(model).filter(model.key == key).first()
            self.session.delete(object)
        self.session.commit()
