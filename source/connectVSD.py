#!/usr/bin/python

# connectVSD 0.1
# (c) Tobias Gass, 2015

import sys
import urllib
import urllib2
import base64
import json
import os
import getpass
sys.path.append('../3rdparty')

from poster import encode_multipart
#from poster.streaminghttp import register_openers

class Folder:
    name=''
    ID=''
    parentFolder=None
    childFolders=None
    level=0

class VSDConnecter:
    url='https://www.virtualskeleton.ch/api'
   
    def __init__(self,*args):
        if (len(args)==0):
            username=raw_input("Username: ")
            password=getpass.getpass()
            self.authstr=base64.encodestring(username+":"+password)
        elif (len(args)==1):
            self.authstr=args[0]
        else:
            self.authstr=base64.encodestring(args[0]+":"+args[1])
        print "Authed : "+self.authstr 
    
    def seturl(self,url):
        self.url=url

    def addAuth(self,req):
        req.add_header("Authorization", "Basic %s" % self.authstr)
        return req

    def getObject(self,ID):
        print self.url+"/files/"+str(ID)
        req=urllib2.Request(self.url+"/objects/"+str(ID))
        self.addAuth(req)
        result=""
        try:
            result=urllib2.urlopen(req)
            return json.load(result)

        except urllib2.URLError as err:
            print "Error retrieving object",ID,err
            #sys.exit()

    def getObjectByUrl(self,url):
        req=urllib2.Request(url)
        self.addAuth(req)
        try:
            result=urllib2.urlopen(req)
            return json.load(result)
        except urllib2.URLError as err:
            print "Error retrieving object",url,err
            sys.exit()
       

    
    def getRequest(self,request):
        req=urllib2.Request(self.url+request)
        self.addAuth(req)
        try:
            result=urllib2.urlopen(req)
            return json.load(result)

        except urllib2.URLError as err:
            print "Error retrieving request",req,"from SMIR:",err
            #sys.exit()

    def optionsRequest(self,request):
        req=urllib2.Request(self.url+request)
        self.addAuth(req)
        req.get_method = lambda: 'OPTIONS' 
        try:
            result=urllib2.urlopen(req).read()
            return json.load(result)

        except urllib2.URLError as err:
            print "Error retrieving request",req,"from SMIR:",err
            #sys.exit()

    def postRequest(self,request,data):
        req=urllib2.Request(self.url+request,data,headers={'Content-Type': 'application/json'})
        self.addAuth(req)
        req.get_method = lambda: 'POST' 
        result=''
        #print req.get_full_url(), req.header_items()
        try:
            result=urllib2.urlopen(req)
            return json.load(result)

        except urllib2.URLError as err:
            print "Error retrieving request",req,"from SMIR:",err
            #sys.exit()

    def putRequest(self,request,data):
        req=urllib2.Request(self.url+request,data,headers={'Content-Type': 'application/json'})
        self.addAuth(req)
        req.get_method = lambda: 'PUT' 
       # print req.get_header()
        try:
            result=urllib2.urlopen(req)
            return json.load(result)
        except urllib2.URLError as err:
            print "Error putting request",req,"from SMIR:",err
            #sys.exit()

    def putRequestSimple(self,request):
        req=urllib2.Request(self.url+request)
        self.addAuth(req)
        req.get_method = lambda: 'PUT' 
       # print req.get_header()
        try:
            result=urllib2.urlopen(req)
            return json.load(result)
        except urllib2.URLError as err:
            print "Error retrieving request",req,"from SMIR:",err
            #sys.exit()

    def downloadFile(self,ID,outputDir="./"):
        d = os.path.dirname(outputDir)
        if not os.path.exists(d):
            os.makedirs(d)

        fileObject=self.getObject(ID)
        filename=outputDir
        for ont in fileObject['ontologyItems']:
            ontology=self.getObjectByUrl(ont['selfUrl'])
            print ontology['term']
            filename+=ontology['term'].replace(" ","_")
        if filename!="":
            filename+="-"
        filename+=str(ID)

        #return filename
        if (fileObject['type']==1):
            #DICOM
            ##create directory
            filename+="/"+os.path.basename(filename)
            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)
            
            count=0
            for ffile in fileObject['files']:
                req=urllib2.Request(ffile['selfUrl']+"/download")
                self.addAuth(req)
                sfilename=filename+"_"+str(count)+".dcm"
                print "Downloading",ffile['selfUrl']+"/download","to",sfilename
                response=""
                try:
                    response=urllib2.urlopen(req)
                except urllib2.URLError as err:
                    print "Error downloading file",ffile['selfUrl'],err
                    sys.exit()


                local_file = open(sfilename, "wb")
                local_file.write(response.read())
                local_file.close()
                count+=1
        else:
            #Nifty?
            for file in fileObject['files']:
                req=urllib2.Request(fileObject['downloadUrl']) #self.url+"/files/"+str(ID)+"/download")
                self.addAuth(req)
                response=""
                try:
                    response=urllib2.urlopen(req)
                except urllib2.URLError as err:
                    print "Error downloading file",ffile['selfUrl'],err
                    sys.exit()
                sfilename=filename+".nii"
                local_file = open(sfilename, "wb")
                local_file.write(response.read())
                local_file.close()
        #dump json object
        local_file = open(filename+".json", "w")
        local_file.write(json.dumps(fileObject))
        local_file.close()


    def getFolderList(self):
        #print self.url+"/folders"
        req=urllib2.Request(self.url+"/folders")
        self.addAuth(req)
        result=""
        try:
            result=json.load(urllib2.urlopen(req))
            return result
        except urllib2.URLError as err:
            print "Error retrieving folders from SMIR:",err
            sys.exit()
    
    def getFolder(self,ID):
        #print self.url+"/folders"
        req=urllib2.Request(self.url+"/folders/"+str(ID))
        self.addAuth(req)
        result=""
        try:
            result=json.load(urllib2.urlopen(req))
            return result
        except urllib2.URLError as err:
            print "Error retrieving folder",ID," from SMIR:",err
            sys.exit()

    def getFileListInFolder(self,ID):
        #print self.url+"/folders"
        req=urllib2.Request(self.url+"/folders/"+str(ID))
        self.addAuth(req)
        result=""
        try:
            result=json.load(urllib2.urlopen(req))
            return result
        except urllib2.URLError as err:
            print "Error retrieving file list for folder",ID,"from SMIR:",err
            #sys.exit()
        

    ##read folder list into linked Folder datastructure
    def readFolders(self,folderList):
    #first pass: create one entry for each folder:
        folderHash={}
        for folder in folderList['items']:
            ID=folder['id']
            folderHash[ID]=Folder()
            folderHash[ID].ID=ID
            folderHash[ID].name=folder['name']
            folderHash[ID].childFolders=[]
       
    #second pass: create references to parent and child folders
        for folder in folderList['items']:
            ID=folder['id']
            if (folder['childFolders']!=None):
            #print folder['childFolders'],ID
                for child in folder['childFolders']:
                    childID=int(child['selfUrl'].split("/")[-1])
                    if (folderHash.has_key(childID)):
                        folderHash[ID].childFolders.append(folderHash[childID])
                if (folder['parentFolder']!=None):
                    parentID=int(folder['parentFolder']['selfUrl'].split("/")[-1])
                    if (folderHash.has_key(parentID)):
                        folderHash[ID].parentFolder=folderHash[parentID]

        return folderHash

    def getFileIDs(self,fileList):
        fileIDList=[]
        for fileObject in fileList['containedObjects']:
            ID=fileObject['selfUrl'].split("/")[-1]
            fileIDList.append(ID)
        return fileIDList

    def uploadFile(self,filenam):
        #register_openers()
        fields={}
        files={'file':{ 'filename' : filenam, 'content':open(filenam,"rb").read()}}
        data,headers=encode_multipart(fields,files)
        req=urllib2.Request(self.url+"/upload",data,headers)
        self.addAuth(req)
        try:
            result=urllib2.urlopen(req)
            return json.load(result)
        except urllib2.URLError as err:
            print "Error uploading",filenam,err
            #sys.exit()

    def addFileToFolder(self,fileID,folderID):
        #get folder object
        folder=self.getFolder(folderID)
        entry={'selfUrl' : self.url+'/objects/'+str(fileID)}
        if folder['containedObjects'] is not None:
            folder['containedObjects'].append(entry)
        else:
            folder['containedObjects']=[]
            folder['containedObjects'].append(entry)
        print folder
        return self.putRequest('/folders',json.dumps(folder))
        

    def addOntologyRelation(self,ontologyRelation):
        oType=ontologyRelation["type"]
        result=self.postRequest('/object-ontologies/'+str(oType),json.dumps(ontologyRelation))
        result2=self.putRequestSimple("/object-ontologies/"+str(oType)+"/"+str(result["id"]))
        return result

    def addOntologyByTypeAndID(self,objectID,oType,oID):
        obj=self.getObject(objectID)
        pos=0
        if obj['ontologyItemRelations'] is not None:
            pos=len(obj['ontologyItemRelations'])

        newRel={"position":pos,"type":oType,"object":{"selfUrl":self.url+'/objects/'+str(objectID)},"ontologyItem":{"selfUrl":self.url+"/ontologies/"+str(oType)+"/"+str(oId)}}
        return self.addOntologyRelation(newRel)
            
    def addLink(self,objectID1,objectID2):
        link={'object1':{'selfurl':self.url+'/objects/'+str(objectID1)} , 'object2':{'selfurl': self.url+'/objects/'+str(objectID2)}}
        return self.postRequest('/object-links',json.dumps(link))

    def uploadSegmentation(self,objectID,segmentationFilename):
        #get original Object
        origObject=self.getObject(objectID)

        #upload Segmentation and get ID
        segFile=self.uploadFile(segmentationFilename)
        print segFile
        print 
        print
        segObjID=int(segFile["relatedObject"]["selfUrl"].split("/")[-1])
        segObj=self.getObject(segObjID)
        print segObj
        print 
        print
        #check if object is segmentation
        maxTries=3
        found=0
        for i in range(maxTries):
            if segObj['type']==2 and segObj['files'][0]['selfUrl']==segFile['file']['selfUrl']:
                print "Found segmentation object with ID",segObj["id"]
                found=1
                break
            else:
                segObjID+=1
                segObj=self.getObject(segObjID)

        if found==0:
            print "Error retrieving segmentation object after upload, aborting"
            sys.exit(0)
        print segObj

        #segObj["type"]=2
        #segObj["
        #self.putRequest("/objects/"+str(segObjID),json.dumps(segObj))

        #link segmentation to original object
        self.addLink(objectID,segObjID)
 
        #add Ontology relations
        for ontRel in origObject['ontologyItemRelations']:
            print "retrieving ontolgy for",ontRel
            print
            print
            ont=self.getObjectByUrl(ontRel['selfUrl'])
            print "found ontology:",ont
            print
            print
            newOntRel={}
            newOntRel["object"]={"selfUrl":self.url+'/objects/'+str(segObjID)}
            newOntRel["type"]=ont["type"]
            newOntRel["ontologyItem"]=ont["ontologyItem"]
            print "Updated ontology to reflect segmentation object:",newOntRel
            print
            print
            print "Uploading Ontology",self.addOntologyRelation(newOntRel)
            print
            print
          
        return segObjID

    def setRightsBasedOnReferenceObject(self,objectID,referenceObjectID):
        #get reference object
        referenceObject=self.getObject(referenceObjectID)
        
        #set group rights
        if referenceObject['objectGroupRights'] is not None:
            for right in referenceObject['objectGroupRights']:
            #get object
                print right
                rightObject=self.getObjectByUrl(right["selfUrl"])
            #create new right with the correct objectID
                newRight={}
                newRight["relatedRights"]=rightObject["relatedRights"]
                newRight["relatedGroup"]=rightObject["relatedGroup"]
                newRight["relatedObject"]={"selfUrl":self.url+"/objects"+str(objectID)}
                self.putRequest("/object-group-rights",json.dumps(newRight))
            
        #set user rights
        if referenceObject['objectUserRights'] is not None:
            
            for right in referenceObject['objectUserRights']:
            #get object
                rightObject=self.getObjectByUrl(right["selfUrl"])
            #create new right with the correct objectID
                newRight={}
                newRight["relatedRights"]=rightObject["relatedRights"]
                newRight["relatedUser"]=rightObject["relatedUser"]
                newRight["relatedObject"]={"selfUrl":self.url+"/objects"+str(objectID)}
                self.putRequest("/object-user-rights",json.dumps(newRight))
                                       
        
     
        


 
                                           