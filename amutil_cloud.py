#Artur Marques, 2022
import boto3
import uuid # UUID objects (universally unique identifiers) according to RFC 4122
from werkzeug.utils import secure_filename
from flask import request
import os.path

#_.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
class AmAwsS3Helper:
    #probabily in the [default] section of the credentials file
    AWS_ACCESS_KEY_ID:str="aws_access_key_id"
    AWS_SECRET_ACCESS_KEY:str="aws_secret_access_key"
    #probably in the [default] section of the config file
    REGION:str="region"

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-04 - created
    receives the path of an AWS config text file
    extracts all the pairs key = value that it finds
    """
    @staticmethod
    def extractAllKVsFromAwsConfigFile(
        pStrAwsConfigFilePath: str,
        pbDebug: bool = True
    ):
        dictKVs = dict()

        bConfigFilePathReceived = os.path.isfile(pStrAwsConfigFilePath)
        if (bConfigFilePathReceived):
            try:
                fr = open(
                    file=pStrAwsConfigFilePath,
                    mode="r"
                )
                listLinesSensitiveContent = fr.readlines()
                fr.close()

                for strLine in listLinesSensitiveContent:
                    strStrippedLine = strLine.strip()
                    bLineStartsWithRectangularOpeningBracket = strStrippedLine.find("[")==0
                    if(not bLineStartsWithRectangularOpeningBracket): #not the opening of a section
                        iEqualPos=strStrippedLine.find("=")
                        if(iEqualPos!=-1):
                            strKey = strStrippedLine[0:iEqualPos-1].strip()
                            strValue = strStrippedLine[iEqualPos+1:].strip()
                            dictKVs[strKey] = strValue
                        #if there was an equal "=" in the line, as in k=v
                    #if line was not a section opening
                #for every line
            except Exception as e:
                if(pbDebug):
                    print(str(e))
                #else
            #except
        #if config file path received

        return dictKVs
    # def extractAllKVsFromAwsConfigFile

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    ACCEPTABLE_ERRORS = [
        "BucketAlreadyOwnedByYou"
    ]

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-03-?? - created
    2022-04-04 - added option to authenticate via explicit credentials and config files
    """
    def __init__(
        self,
        pStrCredentialsFilePath:str="",
        pStrConfigFilePath:str="",
        pbDebug:bool=True
    ):
        bCredentialsFilePathReceived = pStrCredentialsFilePath!="" and os.path.isfile(pStrCredentialsFilePath)
        bConfigFilePathReceived = pStrConfigFilePath!="" and os.path.isfile(pStrConfigFilePath)
        if(bCredentialsFilePathReceived and bConfigFilePathReceived): #only if BOTH!, because the region is a must for explicit bucket creation
            dictCredentials = AmAwsS3Helper.extractAllKVsFromAwsConfigFile(pStrCredentialsFilePath)
            dictConfig = AmAwsS3Helper.extractAllKVsFromAwsConfigFile(pStrConfigFilePath)

            bGotKeyId = AmAwsS3Helper.AWS_ACCESS_KEY_ID in dictCredentials.keys()
            bGotSecret = AmAwsS3Helper.AWS_SECRET_ACCESS_KEY in dictCredentials.keys()
            bGotRegion = AmAwsS3Helper.REGION in dictConfig.keys()

            bGotAllNeeded = bGotKeyId and bGotSecret and bGotRegion

            if (bGotAllNeeded):
                # About creating AWS Buckets
                # Unless your region is in the United States,
                # Define the region *explicitly* when creating a bucket.
                # Or... IllegalLocationConstraintException.
                self.mCurrentSession = boto3.session.Session(
                    aws_access_key_id=dictCredentials[AmAwsS3Helper.AWS_ACCESS_KEY_ID],
                    aws_secret_access_key=dictCredentials[AmAwsS3Helper.AWS_SECRET_ACCESS_KEY],
                    region_name=dictConfig[AmAwsS3Helper.REGION]
                )
            else:
                # provides a session object, authenticated via alternate mechanisms (%userprofile%\credentials or aws configure)
                self.mCurrentSession = boto3.session.Session()
        else:
            # provides a session object, authenticated via alternate mechanisms (%userprofile%\credentials or aws configure)
            self.mCurrentSession = boto3.session.Session()

        self.mbDebug:bool=pbDebug

        self.mS3C = boto3.client('s3') #<class 'botocore.client.S3'>
        if(self.mbDebug):
            print(self.mS3C)
            # <botocore.client.S3 object at 0x00000024B771BB50>
        #if

        self.mS3R = boto3.resource('s3')#<class 'boto3.resources.factory.s3.ServiceResource'>
        if(self.mbDebug):
            print(self.mS3R)
            # s3.ServiceResource()
        #if

        self.mDictBucketConfig = dict()

        bCanCreateBucketConfiguration:bool = self.mCurrentSession and self.mCurrentSession.region_name!=None

        if (bCanCreateBucketConfiguration):

            """
            self.mDictBucketConfig = {
                # "LocationConstraint": "eu-west-1" #'IllegalLocationConstraintException'
                "LocationConstraint": "eu-west-2"  # OK if it matches the config set
            }
            """
            self.mDictBucketConfig = {
                "LocationConstraint":self.mCurrentSession.region_name
            }
        #if could create a config for buckets
    #def __init__

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    @staticmethod
    def genBucketName(
        pStrRelaxedBucketName:str,
        pbAssureUnique:bool=True
    ):
        if(pbAssureUnique):
            oUUID = uuid.uuid4()  # Generate a random UUID #<class 'uuid.UUID'>

            strUUID = str(oUUID)  # UUID object as string #e.g. '6c91e21b-18c4-449b-95e5-c80ec49c9dee'

            strRet = pStrRelaxedBucketName + strUUID  # e.g. 'myBucket6c91e21b-18c4-449b-95e5-c80ec49c9dee'

            listOfStringsToJoin = [pStrRelaxedBucketName, "-", strUUID]
            strRet2 = "".join(listOfStringsToJoin)  # e.g. 'myBucket6c91e21b-18c4-449b-95e5-c80ec49c9dee'

            """
            Example of created name in strRet:
            my-bucketf680820b-d34b-4368-8042-6afb887ca246
            
            Example of created name in strRet2:
            my-bucket-f680820b-d34b-4368-8042-6afb887ca246
            """

            # TODO: observe all naming rules, e.g. AWS bucket names must be [3, 63] symbols long
            return strRet2
        else:
            # TODO: observe all naming rules, e.g. AWS bucket names must be [3, 63] symbols long
            return pStrRelaxedBucketName
        #if-else
    #def genBucketName

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-07 - added an option to configure the created bucket
    """
    def createBucket(
        self,
        pStrRelaxedBucketName:str,
        pbAssureUnique:bool=True,
        pDictBucketConfig:dict=None
    ):
        strUniqueNameForBucket = AmAwsS3Helper.genBucketName(
            pStrRelaxedBucketName=pStrRelaxedBucketName,
            pbAssureUnique=pbAssureUnique
        )

        if(pDictBucketConfig==None):
            pDictBucketConfig=self.mDictBucketConfig
        try:
            theBucket = self.mS3R.create_bucket(
                Bucket=strUniqueNameForBucket,
                #CreateBucketConfiguration=self.mDictBucketConfig
                CreateBucketConfiguration=pDictBucketConfig
            )

            if (self.mbDebug):
                print("Bucket creation result " + str(theBucket))
            # if pbDebug

            return strUniqueNameForBucket, theBucket #tuple
        except Exception as e:
            print(str(e))
            dictError = e.response['Error']
            strErrorCode = dictError['Code']
            bAcceptableError = strErrorCode in AmAwsS3Helper.ACCEPTABLE_ERRORS

            if(bAcceptableError):
                theBucket = self.mS3R.Bucket(
                    name=strUniqueNameForBucket
                )
                return strUniqueNameForBucket, theBucket #tuple
            #if
        # try-except

        return "", None #no name, no bucket if it fails
    # def createBucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02
    renamed from: writeFileToBucketViaResource
    to: uploadLocalFileToBucketViaResource
    """
    def uploadLocalFileToBucketViaResource(
        self,
        pStrBucketName:str,
        pStrFileName:str
    ):
        try:
            #<class 'boto3.resources.factory.s3.Object'>
            theFileObject =\
                self.mS3R.Object(
                    pStrBucketName,
                    pStrFileName
                )

            #upload_file returns None
            uploadResult =\
                theFileObject.upload_file(
                    Filename=pStrFileName
                )

            return True
        except Exception as e:
            print(str(e))
        #try-except

        return False
    #def uploadLocalFileToBucketViaResource

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02 - created
    """
    def createFakeDirectoryPathInBucket(
        self,
        pStrBucketName:str,
        pStrDirPathToCreate:str
    ):
        #dict_keys(['ResponseMetadata', 'ETag'])
        #ETag example: '"d41d8cd98f00b204e9800998ecf8427e"'
        dictRet =\
            self.mS3C.put_object(
                Bucket=pStrBucketName,
                Key=(pStrDirPathToCreate + '/') #by ending in /, "it is a dir", although that concept does not really exist for buckets
            )
        return dictRet
    #def createFakeDirectoryPathInBucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02
    renamed from: writeFileToBucketAltViaResource
    to: uploadLocalFileToBucketAltViaResource
    """
    def uploadLocalFileToBucketAltViaResource(
        self,
        pStrBucketName: str,
        pStrFileName: str
    ):
        try:
            theBucketObjectWithThatName = self.mS3R.Bucket(
                name=pStrBucketName
            )

            #upload_file returns None
            uploadResult = \
                theBucketObjectWithThatName.upload_file(
                    Filename=pStrFileName,
                    Key=pStrFileName
                )

            return True
        except Exception as e:
            if (self.mbDebug):
                print(str(e))
            #if
        #try-except

        return False
    # def uploadLocalFileToBucketAltViaResource

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02
    renamed from: writeFileToBucketViaClient
    to: uploadLocalFileToBucketViaClient
    
    2022-04-03
    added param pStrKeyForObjectAkaDestinationPath,
    to control the name of the destination object, supporting custom paths
    2022-04-05
    added a default value to the 3rd param and made it optional, for retro-compatibility with earlier usage examples
    """
    def uploadLocalFileToBucketViaClient(
        self,
        pStrBucketName: str,
        pStrSourceFileName: str,
        pStrKeyForObjectAkaDestinationPath:str=""
    ):
        if (pStrKeyForObjectAkaDestinationPath==""):
            pStrKeyForObjectAkaDestinationPath=pStrSourceFileName #use same name as source

        try:
            uploadResult = \
                self.mS3C.upload_file(
                    Bucket=pStrBucketName,
                    Filename=pStrSourceFileName,
                    Key=pStrKeyForObjectAkaDestinationPath
                )

            return True
        except Exception as e:
            #on Windows, with temp files: [Errno 13] Permission denied: 'c:\\Temp\\4\\flaskapptev_8kd_'
            print(str(e))
        # try-except

        return False
    # def uploadLocalFileToBucketViaClient

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    DEFAULT_DESTINATION_DIR = "." #was "./dls" until 2022-04-05
    def downloadFileFromBucket(
        self,
        pStrBucketName: str,
        pStrFileName: str,
        pStrDestinationDir:str=DEFAULT_DESTINATION_DIR
    ):
        try:
            theObject = self.mS3R.Object(
                pStrBucketName, #s3 bucket name
                pStrFileName #s3 file name
            )
            if(theObject):
                dlResult =\
                    theObject.download_file(
                        pStrDestinationDir+"/"+pStrFileName
                    )

                return True
            #if
        except Exception as e:
            print(str(e))
        # try-except

        return False
    # def downloadFileFromBucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02 - created
    """
    def readFileInBucket(
        self,
        pStrBucketName: str,
        pStrFileName: str
    ):
        try:
            theObjectInTheBucket = self.mS3R.Object(
                pStrBucketName,
                pStrFileName
            )
            content = theObjectInTheBucket.get()['Body'].read()
            return content
        except Exception as e:
            if(self.mbDebug):
                print(str(e))
        #try-except

        return False
    #def readFileInBucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-03 - created
    """
    def writeContentToFileToBucket(
        self,
        pStrBucketName: str,
        pStrFileName: str,
        pStrContent:str=""
    ):
        try:
            theObjectInTheBucket = self.mS3R.Object(
                pStrBucketName,
                pStrFileName
            )
            strTheWrittenContent = theObjectInTheBucket.put(
                Body=pStrContent
            )
            return strTheWrittenContent
        except Exception as e:
            if (self.mbDebug):
                print(str(e))
        # try-except

        return False
    # def writeContentToFileToBucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-02 - created
    2022-04-04 - changed from static to dynamic
    2022-04-07 - noticed that, after all, had no code to save to local path, so renamed 3rd param to pStrCloudBucketDestinationPath
    """
    def saveFlaskUploadedFileToS3Bucket(
        self,
        pStrBucketName: str,
        pHtmlFileElementName: str,
        pStrCloudBucketDestinationPath: str = "",
        pbAssureUniqueBucketName: bool = False
    ):
        bCheck = request.method == "POST" and request.files[pHtmlFileElementName] != ""

        if (bCheck):
            """
            if the bucket does NOT exist, it is created and returned
            if it exists, it returns the existing bucket
            if the bucket name is invalid, it fails with an exception
            """
            theDestinationBucket = self.createBucket(
                pStrRelaxedBucketName=pStrBucketName,
                pbAssureUnique=pbAssureUniqueBucketName
            )

            if (theDestinationBucket != False):
                # dict_keys(['ResponseMetadata', 'ETag'])
                dictObjectCreationResult = self.createFakeDirectoryPathInBucket(
                    pStrBucketName=pStrBucketName,
                    pStrDirPathToCreate=pStrCloudBucketDestinationPath
                )
                # <class 'werkzeug.datastructures.FileStorage'> #content_length, content_type, filename, headers, mimetye, mimetype_params, name (html name), stream
                fileStorageObjectRepresentingTheUploadedFile = request.files[pHtmlFileElementName]  # e.g. "00.txt"
                strSecureFilename = secure_filename(
                    fileStorageObjectRepresentingTheUploadedFile.filename)  # e.g. "00.txt"

                if (strSecureFilename != ""):
                    saveResultIsAlwaysNone = \
                        fileStorageObjectRepresentingTheUploadedFile.save(
                            dst=strSecureFilename
                        )
                    # strSecureFilename was saved to the system running Flask, so it sets the pStrSourceFileName
                    # TODO: check if file was indeed saved
                    # TODO: save to temporary file and upload the temporary file

                    strDestinationPath = pStrCloudBucketDestinationPath + "/" + strSecureFilename

                    bUploadResult: bool = \
                        self.uploadLocalFileToBucketViaClient(
                            pStrBucketName=pStrBucketName,
                            pStrSourceFileName=strSecureFilename,
                            # RTE: the system cannot find the file is the (local) path is not available
                            pStrKeyForObjectAkaDestinationPath=strDestinationPath
                        )

                return bUploadResult, strSecureFilename
            else:
                return False  # no bucket
        else:
            return False  # not post or no uploaded file
    # def saveFlaskUploadedFileToS3Bucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-07 - created
    2022-04-07 - noticed that, after all, had no code to save to local path, so renamed 3rd param to pStrCloudBucketDestinationPath
    """
    def saveFlaskUploadedPluralFilesToS3Bucket(
        self,
        pStrBucketName: str,
        pHtmlFileElementName: str,
        pStrCloudBucketDestinationPath: str = "",
        pbAssureUniqueBucketName: bool = False
    ):
        dictUploadResults = dict()

        bCheck = request.method == "POST" and request.files[pHtmlFileElementName] != ""

        if (bCheck):
            """
            if the bucket does NOT exist, it is created and returned
            if it exists, it returns the existing bucket
            if the bucket name is invalid, it fails with an exception
            """
            theDestinationBucket = self.createBucket(
                pStrRelaxedBucketName=pStrBucketName,
                pbAssureUnique=pbAssureUniqueBucketName
            )

            if (theDestinationBucket != False):
                # dict_keys(['ResponseMetadata', 'ETag'])
                dictObjectCreationResult = self.createFakeDirectoryPathInBucket(
                    pStrBucketName=pStrBucketName,
                    pStrDirPathToCreate=pStrCloudBucketDestinationPath
                )
                # <class 'werkzeug.datastructures.FileStorage'> #content_length, content_type, filename, headers, mimetye, mimetype_params, name (html name), stream
                listFileStorageObjectsRepresentingTheUploadedFiles:list = request.files.getlist(pHtmlFileElementName)
                for oFileStorageObjectRepresentingSingleUploadedFile in listFileStorageObjectsRepresentingTheUploadedFiles:
                    strSecureFilename:str = secure_filename(
                        oFileStorageObjectRepresentingSingleUploadedFile.filename)  # e.g. "00.txt"

                    if (strSecureFilename != ""):
                        saveResultIsAlwaysNone = \
                            oFileStorageObjectRepresentingSingleUploadedFile.save(
                                dst=strSecureFilename
                            )
                        # strSecureFilename was saved to the system running Flask, so it sets the pStrSourceFileName
                        # TODO: check if file was indeed saved
                        # TODO: save to temporary file and upload the temporary file

                        if(pStrCloudBucketDestinationPath!=""):
                            strDestinationPath = pStrCloudBucketDestinationPath + "/" + strSecureFilename
                        else:
                            strDestinationPath = strSecureFilename
                        #if-else

                        bUploadResult: bool = \
                            self.uploadLocalFileToBucketViaClient(
                                pStrBucketName=pStrBucketName,
                                pStrSourceFileName=strSecureFilename,
                                # RTE: the system cannot find the file if the (local) path is not available
                                pStrKeyForObjectAkaDestinationPath=strDestinationPath
                            )

                        dictUploadResults[strSecureFilename] = bUploadResult
                    #if could get strSecureFilename
                #for every uploaded object
                return dictUploadResults
            else:
                return False  # no bucket
        else:
            return False  # not post or no uploaded file
    # def saveFlaskUploadedPluralFilesToS3Bucket

    # _.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-._.-^-.
    """
    2022-04-07 - created
    Had problems with CORRECT relative (too flask app root) paths.
    The only solution that never failed was writing to absolute paths, so upon call, make sure to joint application.root with desired folder 
    """
    @staticmethod
    def saveFlaskUploadedPluralFilesToFileSystemPath(
        pHtmlFileElementName: str,
        pStrAbsoluteDestinationPath: str = ""
    ):
        dictUploadResults = dict()

        bCheck = request.method == "POST" and request.files[pHtmlFileElementName] != ""

        if (bCheck):
            # <class 'werkzeug.datastructures.FileStorage'> #content_length, content_type, filename, headers, mimetye, mimetype_params, name (html name), stream
            listFileStorageObjectsRepresentingTheUploadedFiles:list = request.files.getlist(pHtmlFileElementName)
            for oFileStorageObjectRepresentingSingleUploadedFile in listFileStorageObjectsRepresentingTheUploadedFiles:
                strSecureFilename:str = secure_filename(
                    oFileStorageObjectRepresentingSingleUploadedFile.filename
                )

                if (strSecureFilename != ""):
                    if (pStrAbsoluteDestinationPath != ""):
                        strDestinationPath = pStrAbsoluteDestinationPath + "/" + strSecureFilename
                    else:
                        strDestinationPath = strSecureFilename
                    #if-else

                    saveResultIsAlwaysNone = \
                        oFileStorageObjectRepresentingSingleUploadedFile.save(
                            dst=strDestinationPath
                            #dst=strSecureFilename
                        )

                    try:
                        fr = open(strDestinationPath, 'rb')
                        dictUploadResults[strSecureFilename]=fr.__sizeof__()
                        #os.path.getsize(strDestinationPath)
                        fr.close()
                    except Exception as e:
                        print(str(e))
                        dictUploadResults[strSecureFilename] = False
                    #try-except
                #if could get strSecureFilename
            #for every uploaded object
            return dictUploadResults
        else:
            return False  # not post or no uploaded file
    # def saveFlaskUploadedPluralFilesToFileSystemPath
#class AmAwsS3Helper