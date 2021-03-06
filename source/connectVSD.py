#!/usr/bin/python

# connectVSD 0.1
# (c) Tobias Gass, 2015
# API documentation: https://demo.virtualskeleton.ch/api/Help/

# system imports
import os
import sys
import urllib2
import base64
import json
import logging

# third party imports

# own imports
from poster import encode_multipart

# code
class ConnectVSDException(Exception):
    """Default exception for connectVSD module."""
    pass

class ConnectionException(ConnectVSDException):
    """Connection or credentials exception."""
    pass

class RequestException(ConnectVSDException):
    """Request execution exception."""
    def __init__(self, message, errors):
        super(RequestException, self).__init__('{} : Signaled reason: {}'.format(message, errors))
    
class Folder:
    name=''
    fullName=''
    ID=''
    parentFolder=None
    childFolders=None
    containedObjects=None
    level=0
    def getFullName(self):
        if self.fullName=='':
            if self.parentFolder==None:
                self.fullName=self.name
            else:
                self.fullName=self.parentFolder.getFullName()+"/"+self.name
        return self.fullName

class VSDConnecter:
    """
    Handler providing convenient methods for the Virtual Skeleton Databases REST
    interface.
    
    !TODO: Describe __init__() here.
    """
    
    url = 'https://www.virtualskeleton.ch/api'
   
    def __init__(self, username = None, password = None, authstr = None):
        if not username is None and not password is None:
            self.authstr = base64.encodestring("{}:{}".format(username, password))
        elif not authstr is None:
            self.authstr = authstr
        else:
            raise ConnectionException('Either username and password or the authstr parameters must be provided.')
        
        logging.info("Authorization string: {}".format(self.authstr))
    
    ################################## MISC ##################################
    
    def setUrl(self, url):
        """Set the server url.
        
        Parameters
        ----------
        url : string
        """
        self.url = url

    def addAuth(self, req):
        """Add the authorization header to a request.
        
        Parameters
        ----------
        req : urllib2.Request
            
        Returns
        -------
        req : urllib2.Request
            The request object with added authorization header.
        """
        req.add_header('Authorization', 'Basic {}'.format(self.authstr))
        return req
    
    
    ################################## REST-METHODS ##################################

    def getBySelfUrl(self, selfurl):
        """Get the JSON description of a single resource.
        
        Parameters
        ----------
        selfurl : string
            The selfUrl identifier.
            
        Returns
        -------
        objjson : dict
            The object behind the url described by a dict constructed from
            the servers JSON response.
        """
        req = urllib2.Request(selfurl)
        return self.__execute_request(req)

    def getObject(self, oid):
        """Get the JSON description of a single object.
        
        Parameters
        ----------
        oid : int
            The objects id.
            
        Returns
        -------
        objjson : dict
            The object described by a dict constructed from the servers JSON
            response.
        """
        #!TODO: What happens if the id is wrong? Will there still be some value returned.
        return self.getRequest('/objects/{}'.format(oid))

    def uploadFile(self, filename):
        """Upload a file.
        
        Parameters
        ----------
        filename : string
            Path to the file to upload.
            
        Returns
        -------
        objjson : dict
            The server response as JSON dict.
        """
        fields={}
        files={'file':{ 'filename' : filename, 'content': open(filename, "rb").read()}}
        data, headers = encode_multipart(fields, files)
        req = urllib2.Request('{}/upload'.format(self.url), data, headers)
        return self.__execute_request(req)
    
    def deleteObject(self, oid):
        """Delete an (unpublished) object.
        
        Parameters
        ----------
        oid : int
            The objects id.
        """
        return self.deleteRequest('/objects/{}'.format(oid))
    
    def getFolder(self, fid):
        """Get the JSON description of a single object.
        
        Parameters
        ----------
        fid : int
            The folders id.
            
        Returns
        -------
        Returns
        -------
        objjson : dict
            The folder described by a dict constructed from the servers JSON
            response.
        """
        return self.getRequest('/folders/{}'.format(fid))
    
    def addObjectToFolder(self, oid, fid):
        """Add an object to an folder.
        
        Parameters
        ----------
        oid : int
            The objects id.
        fid : int
            The folders id.
            
        Returns
        -------
        objjson : dict
            The server response as JSON dict.
        """
        folder = self.getFolder(fid)
        entry = {'selfUrl': '{}/objects/{}'.format(fid, oid)}
        if folder['containedObjects'] is not None:
            folder['containedObjects'].append(entry)
        else:
            folder['containedObjects'] = [entry]
        return self.putRequest('/folders', json.dumps(folder))    

    def addOntology(self, oid, ontotype, ontoid):
        """Add an ontoloy to an object.
        
        Parameters
        ----------
        oid : int
            The objects id.
        ontotype : int
            The ontology type.
        ontoid : int
            The ontology id.
            
        Returns
        -------
        objjson : dict
            The server response as JSON dict.
        """
        obj = self.getObject(oid)
        pos = 0
        if obj['ontologyItemRelations'] is not None:
            pos = len(obj['ontologyItemRelations'])

        onto_relation = {'position': pos,
                         'type': ontotype,
                         'object': {'selfUrl': '{}/objects/{}'.format(self.url, oid)},
                         'ontologyItem': {'selfUrl': '{}/ontologies/{}/{}'.format(self.url, ontotype, ontoid)}}
        return self.postRequest('/object-ontologies/{}'.format(ontotype), json.dumps(onto_relation))

    def addLink(self, oid1, oid2, description = ""): # !TODO: description is accepted, but does not seem to be settable
        """Create a link between two objects.
        
        Parameters
        ----------
        oid1 : int
            The first objects id.
        oid2 : int
            The second objects id.
        description : string
            Optional description for the link.
    
        Returns
        -------
        Returns
        -------
        objlinksjson : dict
            The server response as JSON dict.
        """
        link = {'object1': {'selfUrl': '{}/objects/{}'.format(self.url, oid1)},
                'object2': {'selfUrl': '{}/objects/{}'.format(self.url, oid2)},
                'description': description}
        return self.postRequest('/object-links', json.dumps(link))

    def generateBaseFilenameFromOntology(self,ID,prefix=""):
        fileObject=self.getObject(ID)
        filename=prefix
        for ont in fileObject['ontologyItems']:
            ontology=self.getObjectByUrl(ont['selfUrl'])
            print ontology['term']
            filename+=ontology['term'].replace(" ","_")
        if filename!="":
            filename+="-"
        filename+=str(ID)
        return filename

    
    def downloadFile(self,ID,filename,dryRun=False):
        d = os.path.dirname(filename)
        if not os.path.exists(d):
            os.makedirs(d)

        fileObject=self.getObject(ID)
       

        #return filename
        #if (fileObject['type']==1):
        if (len(fileObject['files'])>1):
            #DICOM
            ##create directory
            filename+="/"+os.path.basename(filename)
            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)
            
            count=0
            if fileObject['name']!=None:
                extension=fileObject['name'].split(".")[-1]
            else:
                extension="dcm"
            for ffile in fileObject['files']:
                req=urllib2.Request(ffile['selfUrl']+"/download")
                self.addAuth(req)
                sfilename=filename+"_"+str(count)+"."+extension
                if not os.path.exists(sfilename):
                    print "Downloading",ffile['selfUrl']+"/download","to",sfilename
                    if not dryRun:
                        response=""
                        try:
                            response=urllib2.urlopen(req)
                        except urllib2.URLError as err:
                            print "Error downloading file",ffile['selfUrl'],err
                            sys.exit()
                        
                        local_file = open(sfilename, "wb")
                        local_file.write(response.read())
                        local_file.close()
                else:
                    print "File",sfilename,"already exists, skipping"
                count+=1
        else:
            #SINGLE FILE
            #get actual file object
            
            fileObj=self.getObjectByUrl( fileObject['files'][0]['selfUrl'])
            #print fileObject['id']
            #print fileObj['id']
            if fileObject['name']!=None:
                extension=fileObject['name'].split(".")[-1]
            else:
                extension="nii"
            sfilename=filename+"."+extension
            if not os.path.exists(sfilename):
                req=urllib2.Request(fileObj['downloadUrl']) #self.url+"/files/"+str(ID)+"/download")
                print "Downloading",fileObj['downloadUrl'],"to",sfilename
                self.addAuth(req)
                response=""
                if not dryRun:
                    try:
                        response=urllib2.urlopen(req)
                    except urllib2.URLError as err:
                        print "Error downloading file",ffile['selfUrl'],err
                        sys.exit()
           
                    local_file = open(sfilename, "wb")
                    local_file.write(response.read())
                    local_file.close()
            


        

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
            if (not folder['containedObjects']==None):
                folderHash[ID].containedObjects={}
                for obj in folder['containedObjects']:
                    objID=obj['selfUrl'].split("/")[-1]
                    folderHash[ID].containedObjects[objID]=obj['selfUrl']

        #third pass: gett full path names in folder hierarchy
        for key, folder in folderHash.iteritems():
            folder.getFullName()

        return folderHash

    def getFileIDs(self,fileList):
        fileIDList=[]
        for fileObject in fileList['containedObjects']:
            ID=fileObject['selfUrl'].split("/")[-1]
            fileIDList.append(ID)
        return fileIDList
            


    def getLinkedSegmentation(self,objectID):
        result=None
        obj=self.getObject(objectID)
        for link in obj['linkedObjects']:
            linkedObject=self.getObjectByUrl(link['selfUrl'])
            if linkedObject['type']==2:
                result=linkedObject['id']
        return result


    def uploadSegmentation(self,segmentationFilename):
       
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
        return segObjID

    def setOntologyBasedOnReferenceObject(self,targetObjectID, origObjectID):
        origObject=self.getObject(origObjectID)

        #add Ontology relations
        for ontRel in origObject['ontologyItemRelations']:
            #print "retrieving ontolgy for relation ",ontRel
            #print
            ont=self.getObjectByUrl(ontRel['selfUrl'])
            #print "found ontology relation:",ont
            #print
            newOntRel={}
            newOntRel["object"]={"selfUrl":self.url+'/objects/'+str(targetObjectID)}
            newOntRel["type"]=ont["type"]
            newOntRel["position"]=ont["position"]
            newOntRel["ontologyItem"]=ont["ontologyItem"]
            #print "Updated ontology to reflect segmentation object:",newOntRel
            #print
            #print "Uploading Ontology"
            result=self.addOntologyRelation(newOntRel)
            #print "done, result:",result
            #print
            #print
            #print
       

    def setRightsBasedOnReferenceObject(self,objectID,referenceObjectID):
        #get reference object
        referenceObject=self.getObject(referenceObjectID)
        
        #set group rights
        print "Setting group rights"
        if referenceObject['objectGroupRights'] is not None:
            for right in referenceObject['objectGroupRights']:
            #get object
                rightObject=self.getObjectByUrl(right["selfUrl"])
               #create new right with the correct objectID
                newRight={}
                newRight["relatedRights"]=rightObject["relatedRights"]
                newRight["relatedGroup"]=rightObject["relatedGroup"]
                newRight["relatedObject"]={"selfUrl":self.url+"/objects/"+str(objectID)}
                self.postRequest("/object-group-rights",json.dumps(newRight))
            
        #set user rights
        print "Setting user rights"
        if referenceObject['objectUserRights'] is not None:
            
            for right in referenceObject['objectUserRights']:
            #get object
                rightObject=self.getObjectByUrl(right["selfUrl"])
            #create new right with the correct objectID
                newRight={}
                newRight["relatedRights"]=rightObject["relatedRights"]
                newRight["relatedUser"]=rightObject["relatedUser"]
                newRight["relatedObject"]={"selfUrl":self.url+"/objects"+str(objectID)}
                self.postRequest("/object-user-rights",json.dumps(newRight))
                                       
        
    ################################## REQUESTS ##################################
        
    def getRequest(self, request):
        """Execute a single GET request on the server.
        
        Parameters
        ----------
        request : string
        
        Returns
        -------
        response : dict
            The server response interpreted as JSON object.
        """
        req = urllib2.Request('{}/{}'.format(self.url, request))
        return self.__execute_request(req)

    def optionsRequest(self, request):
        """Execute a single OPTIONS request on the server.
        
        Parameters
        ----------
        request : string
        
        Returns
        -------
        response : dict
            The server response interpreted as JSON object.
        """
        req = urllib2.Request('{}/{}'.format(self.url, request))
        req.get_method = lambda: 'OPTIONS' 
        return self.__execute_request(req)

    def postRequest(self, request, data):
        """Execute a single POST request on the server.
        
        Parameters
        ----------
        request : string
        data : string
            A string containing data in JSON format.
        
        Returns
        -------
        response : dict
            The server response interpreted as JSON object.
        """
        req = urllib2.Request('{}/{}'.format(self.url, request),
                              data, headers={'Content-Type': 'application/json'})
        req.get_method = lambda: 'POST' 
        return self.__execute_request(req)

    def putRequest(self, request, data = None):
        """Execute a single PUT request on the server.
        
        Parameters
        ----------
        request : string
        data : string
            A string containing data in JSON format.
        
        Returns
        -------
        response : dict
            The server response interpreted as JSON object.
        """        
        if data is None:
            req = urllib2.Request('{}/{}'.format(self.url, request))
        else:
            req = urllib2.Request('{}/{}'.format(self.url, request),
                                  data, headers={'Content-Type': 'application/json'})
        req.get_method = lambda: 'PUT' 
        return self.__execute_request(req)
    
    def deleteRequest(self, request):
        """Execute a single DELETE request on the server.
        
        Parameters
        ----------
        request : string
        """
        req = urllib2.Request('{}/{}'.format(self.url, request))
        req.get_method = lambda: 'DELETE' 
        self.__execute_request(req, return_json = False)    
        
    def __execute_request(self, req, return_json = True):
        """Send a request to the server."""
        self.addAuth(req)
        try:
            result = urllib2.urlopen(req)
            if return_json:
                return json.load(result)
            else:
                return
        except urllib2.URLError as err:
            raise RequestException('Error executing {} request {}'.format(req.get_method(), req.get_full_url()), err)


 
                                           
