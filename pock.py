import requests
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper


def HttpClient(url=c.BLANK) :
    clientUrl = url
    def Wrapper(OuterClass, *args, **kwargs):
        class InnerClass(OuterClass):
            url = clientUrl
            def __init__(self,*args, **kwargs):
                OuterClass.__init__(self,*args, **kwargs)
            def myPrint(self, *args, **kwargs):
                raise HttpClientEvent(*args, key=4, **kwargs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        print(InnerClass)
        return InnerClass
    return Wrapper


class HttpClientEvent(Exception):
    def __init__(self, *args, key=0, **kwargs):
        Exception.__init__(self, 'HttpClientEvent')
        self.key = key
        self.args = args
        self.kwargs = kwargs


def getHttpClientEvent(resourceInstanceMethod, *args, **kwargs):
    try:
        return resourceInstanceMethod(*args, **kwargs)
    except HttpClientEvent as httpClientEvent:
        return httpClientEvent
    raise Exception('HttpClientEvent not found')


def HttpClientMethod(
    url = c.BLANK
):
    clientMethodUrl = url
    def innerMethodWrapper(resourceInstanceMethod, *args, **kwargs) :
        def myPrint(resourceInstance, abcd):
            url = 2
            if ObjectHelper.isNotNone(abcd):
                url = resourceInstance.url + clientMethodUrl + abcd
            return url
        def innerResourceInstanceMethod(*args, **kwargs):
            resourceInstance = args[0]
            completeResponse = 1
            httpClientEvent = getHttpClientEvent(resourceInstanceMethod, *args, **kwargs)
            try:
                return myPrint(resourceInstance, *httpClientEvent.args ,**httpClientEvent.kwargs)
            except Exception as exception:
                print(exception)
                completeResponse = 3
                return completeResponse
            return completeResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = clientMethodUrl
        return innerResourceInstanceMethod
    return innerMethodWrapper

@HttpClient(url='/uri-1')
class MyClass:

    @HttpClientMethod(url='/uri-2')
    def getSomething(self, abcd):
        completeResponse = 2
        print('before my print')
        completeResponse = self.myPrint(abcd)
        print('after my print')
        return completeResponse

print('start')
myInstance = MyClass()
completeResponse = myInstance.getSomething('/like/this')
print(f'completeResponse: {completeResponse}')
print('finish')
