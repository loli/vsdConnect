# nose-tests for  connectVSD 0.1
# (c) Oskar Maier, 2015
# (c) Tobias Gass, 2015

import urllib2
import base64

from nose import with_setup
from nose.tools import assert_raises

import connectVSD

class TestConnectVSD:
    
    __username = "demo@virtualskeleton.ch"
    __password = "demo"
    __server = "https://demo.virtualskeleton.ch/api"
    
    __dummyusername = "user"
    __dummypassword = "password"
    __dummyserver = "http://www.google.de"
    
    connection = None
    
    @classmethod
    def setup_class(cls):
        """
        Set-up executed once before any test is run.
        """
        pass
    
    def setup(self):
        """
        Set-up executed before each test.
        """
        self.connection = connectVSD.VSDConnecter(self.__username, self.__password)
        self.connection.setUrl(self.__server)
    
    def test_init(self):
        connection = connectVSD.VSDConnecter(self.__dummyusername, self.__dummypassword)
        assert connection.authstr == base64.encodestring("{}:{}".format(self.__dummyusername, self.__dummypassword))
        
        authstr = base64.encodestring("{}:{}".format(self.__dummyusername, self.__dummypassword))
        connection = connectVSD.VSDConnecter(authstr = authstr)
        assert connection.authstr == authstr
        
        with assert_raises(connectVSD.ConnectionException):
            connectVSD.VSDConnecter()
            
        with assert_raises(connectVSD.ConnectionException):
            connectVSD.VSDConnecter(self.__dummyusername)
            
        with assert_raises(connectVSD.ConnectionException):
            connectVSD.VSDConnecter(username = self.__dummyusername)
            
        with assert_raises(connectVSD.ConnectionException):
            connectVSD.VSDConnecter(password = self.__dummypassword)
    
    def test_setUrl(self):
        url = "https://just.a-test.sw"
        self.connection.setUrl(url)
        assert url == self.connection.url
        
    def test_addAuth(self):
        req = urllib2.Request(self.__dummyserver)
        req = self.connection.addAuth(req)
        assert req.get_header('Authorization') is not None
        assert self.connection.authstr in req.get_header('Authorization')
        
    def test_getObject(self):
        # first: create object
        # then: get object
        pass
    
    
