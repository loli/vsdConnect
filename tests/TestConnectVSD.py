# nose-tests for  connectVSD 0.1
# (c) Oskar Maier, 2015
# (c) Tobias Gass, 2015

import urllib2
import base64
import sys

from nose.tools import assert_raises

import connectVSD

class TestConnectVSD:
    
    __username = "demo@virtualskeleton.ch"
    __password = "demo"
    __server = "https://demo.virtualskeleton.ch/api"
    
    __testfolder = 38 # e.g. myprojects-folder
    
    __dummyusername = "user"
    __dummypassword = "password"
    __dummyserver = "http://www.google.de"
    
    __testfile = "tests/resources/image.nii"
    __testfile_invalid = "tests/resources/image.xyz"
    
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
        
    def test_uploadFile(self):
        resp = self.connection.uploadFile(self.__testfile)
        assert resp is not None
        
        with assert_raises(connectVSD.RequestException):
            self.connection.uploadFile(self.__testfile_invalid)
        
    def test_getObject(self):
        resp1 = self.connection.uploadFile(self.__testfile)
        oid = resp1['relatedObject']['selfUrl'].split('/')[-1]
        resp2 = self.connection.getObject(oid)
        assert resp2 is not None
        assert int(oid) == resp2['id']
        
        with assert_raises(connectVSD.RequestException):
            self.connection.getObject(sys.maxint)
        
    def test_deleteObject(self):
        resp1 = self.connection.uploadFile(self.__testfile)
        oid = resp1['relatedObject']['selfUrl'].split('/')[-1]
        self.connection.deleteObject(oid)
        
        with assert_raises(connectVSD.RequestException):
            self.connection.deleteObject(sys.maxint)
            
    def test_getFolder(self):
        resp = self.connection.getFolder(self.__testfolder)
        assert resp is not None
        assert self.__testfolder == resp['id']
        
        with assert_raises(connectVSD.RequestException):
            self.connection.getFolder(sys.maxint)
            
    def test_addLink(self):
        resp1 = self.connection.uploadFile(self.__testfile)
        oid1 = resp1['relatedObject']['selfUrl'].split('/')[-1]
        resp2 = self.connection.uploadFile(self.__testfile)
        oid2 = resp2['relatedObject']['selfUrl'].split('/')[-1]
        resp3 = self.connection.addLink(oid1, oid2, description = "xxx")
        assert resp3 is not None
        
    
