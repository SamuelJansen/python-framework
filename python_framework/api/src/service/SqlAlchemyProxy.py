import os, time

from python_helper import Constant as c
from python_helper import SettingHelper, EnvironmentHelper, ObjectHelper, StringHelper, log, Method, Function, ReflectionHelper

import sqlalchemy
from sqlalchemy import create_engine, exists, select
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, close_all_sessions
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, Column, Numeric, Integer, String, Float, ForeignKey, UnicodeText, MetaData, Sequence, DateTime, Date, Time, Interval, Boolean
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
Numeric = Numeric

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
    SELF = 'SELF'
    INIT = 'INIT'
    ATTACH = 'ATTACH'
    LOAD = 'LOAD'
    REFRESH = 'REFRESH'
    EXPIRE = 'EXPIRE'
    DETEACHED_TO_PERSISTENT = 'DETEACHED_TO_PERSISTENT'
    TRANSIENT_TO_PENDING = 'TRANSIENT_TO_PENDING'
    PENDING_TO_TRANSIENT = 'PENDING_TO_TRANSIENT'
    PERSISTENT_TO_TRANSIENT = 'PERSISTENT_TO_TRANSIENT'
    IMPLEMENTED_QUERY = 'IMPLEMENTED_QUERY'
    UNKNOWN = 'UNKNOWN'

def onInitListener(target, args, kwargs):
    target.__onInit__(args, kwargs)

def onAttachListener(session, target):
    target.__onAttach__(session)

def onLoadListener(target, context):
    target.__onLoad__(context)

def onRefreshListener(target, context, attributes):
    target.__onRefresh__(context, attributes)

def onExpireListener(target, attributes):
    target.__onExpire__(attributes)

def onDeteachedToPersistentListener(session, target):
    target.__onDeteachedToPersistent__(session)

def onTransientToPendingListener(session, target):
    target.__onTransientToPending__(session)

def onPendingToTransientListener(session, target):
    target.__onPendingToTransient__(session)

def onPersistentToTransientListener(session, target):
    target.__onPersistentToTransient__(session)

# def onAppendWoMutationListener(target, targetList, initiator):
#     onAppendWoMutation(target)
#     onAppendWoMutation(targetList)
#
# def onBulkReplaceListener(target, targetList, initiator):
#     onAppendWoMutation(target)
#     onAppendWoMutation(targetList)

def getNewOriginalModel():
    return declarative_base()

class PythonFramworkBaseClass(getNewOriginalModel()):
    __abstract__ = True
    def __onChange__(self, *args, eventType=OnORMChangeEventType.UNKNOWN, **kwargs):
        return self
    def __safelyOnChange__(self, *args, eventType=OnORMChangeEventType.UNKNOWN, **kwargs):
        try:
            self.__onChange__(*args, eventType=eventType, **kwargs)
        except Exception as exception:
            log.warning(self.__safelyOnChange__, 'Not possible to handle __onChange__ properly', exception=exception)
        return self
    def __onInit__(self, args, kwargs):
        self.__safelyOnChange__(args, kwargs, eventType=OnORMChangeEventType.INIT)
    def __onAttach__(self, session):
        self.__safelyOnChange__(session, eventType=OnORMChangeEventType.ATTACH)
    def __onLoad__(self, context):
        self.__safelyOnChange__(context, eventType=OnORMChangeEventType.LOAD)
    def __onRefresh__(self, context, attributes):
        self.__safelyOnChange__(context, attributes, eventType=OnORMChangeEventType.REFRESH)
    def __onExpire__(self, attrs):
        self.__safelyOnChange__(attrs, eventType=OnORMChangeEventType.EXPIRE)
    def __onDeteachedToPersistent__(self, session):
        self.__safelyOnChange__(session, eventType=OnORMChangeEventType.DETEACHED_TO_PERSISTENT)
    def __onTransientToPending__(self, session):
        self.__safelyOnChange__(session, eventType=OnORMChangeEventType.TRANSIENT_TO_PENDING)
    def __onPendingToTransient__(self, session):
        self.__safelyOnChange__(session, eventType=OnORMChangeEventType.PENDING_TO_TRANSIENT)
    def __onPersistentToTransient__(self, session):
        self.__safelyOnChange__(session, eventType=OnORMChangeEventType.PERSISTENT_TO_TRANSIENT)

    def setDefaultValues(self, *args, eventType=OnORMChangeEventType.SELF, **kwargs):
        return self.__safelyOnChange__(*args, eventType=eventType, **kwargs)
    def loadDefaultValues(self, *args, eventType=OnORMChangeEventType.SELF, **kwargs):
        return self.setDefaultValues(*args, eventType=eventType, **kwargs)
    def reload(self, *args, eventType=OnORMChangeEventType.SELF, **kwargs):
        return self.setDefaultValues(*args, eventType=eventType, **kwargs)


@Function
def handleOnChange(instanceOrInstanceList):
    if ObjectHelper.isNone(instanceOrInstanceList):
        return instanceOrInstanceList
    elif isinstance(instanceOrInstanceList, PythonFramworkBaseClass) or isinstance(instanceOrInstanceList, DeclarativeMeta):
        instanceOrInstanceList.reload(eventType=OnORMChangeEventType.IMPLEMENTED_QUERY)
    elif (ObjectHelper.isCollection(instanceOrInstanceList) and ObjectHelper.isNotDictionary(instanceOrInstanceList)) or type(instanceOrInstanceList) == InstrumentedList:
        for i in instanceOrInstanceList:
            handleOnChange(i)
    return instanceOrInstanceList

@Function
def getNewModel():
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

###- deprecated
def isNeitherNoneNorBlank(thing):
    return ObjectHelper.isNeitherNoneNorBlank(thing)

###- deprecated
def isNoneOrBlank(thing):
    return ObjectHelper.isNoneOrBlank(thing)

def getUnitCondition(query: dict, modelClass):
    return {
        k: v
        for k, v in query.items()
        if (not k.endswith(LIST)) and ObjectHelper.isNotEmpty(v)
    }

def getCollectionCondition(query: dict, modelClass, additionalCondition=None):
    condition = True
    for k, v in query.items():
        if k.endswith(LIST) and ObjectHelper.isNotEmpty(v):
            condition = and_(
                condition,
                ReflectionHelper.getAttributeOrMethod(modelClass, k.replace(LIST, c.BLANK)).in_(v)
            )
    if ObjectHelper.isNotNone(additionalCondition):
        condition = and_(
            additionalCondition,
            condition
        )
    return condition


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
        self.context = []
        self.sqlalchemy = sqlalchemy
        dialect = self.globals.getSetting(f'{self.KW_API}{c.DOT}{self.KW_DATABASE}{c.DOT}{self.KW_REPOSITORY_DIALECT}')
        self.engine = self.getNewEngine(dialect, echo, connectArgs)
        self.model = model
        self.model.metadata.bind = self.engine
        self.session = self.getNewSession()
        # self.model.metadata.reflect()
        # self.run()

    def getNewSession(self):
        session = scoped_session(sessionmaker(self.engine)) ###- sessionmaker(bind=self.engine)()
        # session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine)) ###- sessionmaker(bind=self.engine)()
        event.listen(PythonFramworkBaseClass, 'load', onLoadListener, propagate=True, restore_load_context=True)
        event.listen(PythonFramworkBaseClass, 'refresh', onRefreshListener, restore_load_context=True)
        event.listen(PythonFramworkBaseClass, 'init', onInitListener)
        event.listen(PythonFramworkBaseClass, 'expire', onExpireListener)
        event.listen(session, 'before_attach', onAttachListener)
        event.listen(session, "detached_to_persistent", onDeteachedToPersistentListener)
        event.listen(session, "transient_to_pending", onTransientToPendingListener)
        event.listen(session, "pending_to_transient", onPendingToTransientListener)
        event.listen(session, "persistent_to_transient", onPersistentToTransientListener)
        # event.listen(someAttribute, "append_wo_mutation", onAppendWoMutationListener)
        # event.listen(someAttribute, "bulk_replace", onBulkReplaceListener)
        return session
        
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
        if ObjectHelper.isNeitherNoneNorBlank(url):
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
            if ObjectHelper.isNeitherNoneNorBlank(url):
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
                if ObjectHelper.isNeitherNoneNorBlank(username) and ObjectHelper.isNeitherNoneNorBlank(password):
                    url += f'{username}{c.COLON}{password}'
                if ObjectHelper.isNeitherNoneNorBlank(host) and ObjectHelper.isNeitherNoneNorBlank(port):
                    url += f'{c.ARROBA}{host}{c.COLON}{port}'
                url += c.SLASH
                database = f'{database}' if ObjectHelper.isNeitherNoneNorBlank(database) else f'{self.DEFAULT_LOCAL_STORAGE_NAME if ObjectHelper.isNone(self.globals.apiName) else self.globals.apiName}{c.DOT}{self.EXTENSION}'
                if not ObjectHelper.isNeitherNoneNorBlank(dialect):
                    dialect = self.DEFAULT_DIALECT
                plusDriverOrNothing = f'{c.PLUS}{driver}' if ObjectHelper.isNeitherNoneNorBlank(driver) else c.NOTHING
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
    def flush(self, session=None):
        if ObjectHelper.isNotNone(session):
            session.flush()
            return
        if ObjectHelper.isNotNone(self.session):
            self.session.flush()

    @Method
    def rollback(self, session=None):
        if ObjectHelper.isNotNone(session):
            session.rollback()
            return
        if ObjectHelper.isNotNone(self.session):
            self.session.rollback()

    @Method
    def commit(self, session=None):
        if ObjectHelper.isNotNone(session):
            session.commit()
            return
        if ObjectHelper.isNotNone(self.session):
            self.session.commit()

    @Method
    def load(self, modelOrModelList):
        return handleOnChange(modelOrModelList)

    @Method
    def getContext(self):
        return self.load(self.context)

    @Method
    def backupContext(self):
        try:
            context = self.getContext()
            for instance in self.session.dirty:
                if instance not in context:
                    context.append(self.load(instance))
        except Exception as exception:
            log.warning(self.backupContext, 'Not possible backup context', exception=exception)

    @Method
    def reloadContextFromBackup(self):
        try:
            for instance in self.getContext():
                self.context.pop(self.context.index(instance))
                if instance not in self.session.dirty:
                    self.session.dirty.add(instance)
        except Exception as exception:
            log.warning(self.reloadContextFromBackup, 'Not possible reload context backup', exception=exception)

    @Method
    def getQueryFilter(self, query, modelClass, joinList=None, additionalCondition=None, session=None):
        if ObjectHelper.isNone(session):
            session = self.session
        sessionQuery = session.query(modelClass)
        if ObjectHelper.isNotEmpty(joinList):
            for join in joinList:
                sessionQuery.join(join)
        return session.query(modelClass).filter(
            getCollectionCondition(
                query,
                modelClass,
                additionalCondition = additionalCondition
            )
        ).filter_by(
            **getUnitCondition(query, modelClass)
        )

    @Method
    def save(self, instance):
        self.load(instance)
        self.session.add(instance)
        return self.load(instance)

    @Method
    def saveNew(self, *args):
        modelClass = args[-1]
        return self.save(modelClass(*args[:-1]))

    @Method
    def saveAndCommit(self, instance):
        self.save(instance)
        self.session.commit()
        return self.load(instance)

    @Method
    def saveNewAndCommit(self, *args):
        modelClass = args[-1]
        return self.saveAndCommit(modelClass(*args[:-1]))

    @Method
    def saveAll(self, instanceList):
        self.load(instanceList)
        self.session.add_all(instanceList)
        return self.load(instanceList)

    @Method
    def saveAllAndCommit(self, instanceList):
        self.saveAll(instanceList)
        self.session.commit()
        return self.load(instanceList)

    @Method
    def findAll(self, modelClass):
        instanceList = self.session.query(modelClass).all()
        return self.load(instanceList)

    @Method
    def findAllAndCommit(self, modelClass):
        instanceList = self.findAll(modelClass)
        self.session.commit()
        return self.load(instanceList)

    @Method
    def findByIdAndCommit(self, id, modelClass):
        instance = self.session.query(modelClass).filter(modelClass.id == id).first()
        self.session.commit()
        return self.load(instance)

    @Method
    def findAllByIdAndCommit(self, id, modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.id == id).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def findAllByIdInAndCommit(self, idList, modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.id.in_(idList)).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def existsByIdAndCommit(self, id, modelClass):
        # ret = Session.query(exists().where(and_(Someobject.field1 == value1, Someobject.field2 == value2)))
        objectExists = self.session.query(exists().where(modelClass.id == id)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByKeyAndCommit(self, key, modelClass):
        instance = self.session.query(modelClass).filter(modelClass.key == key).first()
        self.session.commit()
        return self.load(instance)

    @Method
    def findAllByKeyAndCommit(self, key, modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.key == key).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def findAllByKeyInAndCommit(self, keyList, modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.key.in_(keyList)).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def existsByKeyAndCommit(self, key, modelClass):
        objectExists = self.session.query(exists().where(modelClass.key == key)).one()[0]
        self.session.commit()
        return objectExists

    @Method
    def findByStatusAndCommit(self,status,modelClass):
        instance = self.session.query(modelClass).filter(modelClass.status == status).first()
        self.session.commit()
        return self.load(instance)

    @Method
    def findAllByStatusAndCommit(self,status,modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.status == status).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def findAllByStatusInAndCommit(self, statusList, modelClass):
        instanceList = self.session.query(modelClass).filter(modelClass.status.in_(statusList)).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def existsByQueryAndCommit(self, query, modelClass, joinList=None, additionalCondition=None):
        exists = self.session.query(
            literal(True)
        ).filter(
            self.getQueryFilter(
                query,
                modelClass,
                joinList = joinList,
                additionalCondition = additionalCondition
            ).exists()
        ).scalar()
        self.session.commit()
        return exists

    @Method
    def findAllByQueryAndCommit(self, query, modelClass, joinList=None, additionalCondition=None):
        instanceList = []
        if ObjectHelper.isNotNone(query):
            instanceList = self.getQueryFilter(
                query,
                modelClass,
                joinList = joinList,
                additionalCondition = additionalCondition
            ).all()
        self.session.commit()
        return self.load(instanceList)

    @Method
    def deleteByIdAndCommit(self, id, modelClass):
        if self.session.query(exists().where(modelClass.id == id)).one()[0] :
            instance = self.session.query(modelClass).filter(modelClass.id == id).first()
            self.session.delete(instance)
        self.session.commit()

    @Method
    def deleteByKeyAndCommit(self, key, modelClass):
        if self.session.query(exists().where(modelClass.key == key)).one()[0] :
            instance = self.session.query(modelClass).filter(modelClass.key == key).first()
            self.session.delete(instance)
        self.session.commit()

    @Method
    def deleteAndCommit(self, instance):
        self.session.delete(instance)
        self.session.commit()

    @Method
    def deleteAllByIdIn(self, objectIdList, modelClass):
        self.session.query(modelClass).filter(modelClass.id.in_(objectIdList)).delete(synchronize_session=False)

    @Method
    def deleteAllByKeyIn(self, objectKeyList, modelClass):
        self.session.query(modelClass).filter(modelClass.key.in_(objectKeyList)).delete(synchronize_session=False)

    @Method
    def deleteAllByIdInAndCommit(self, objectIdList, modelClass):
        self.deleteAllByIdIn(objectIdList, modelClass)
        self.session.commit()

    @Method
    def deleteAllByKeyInAndCommit(self, objectKeyList, modelClass):
        self.deleteAllByKeyIn(objectKeyList, modelClass)
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
