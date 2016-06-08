import sys
import pysvn
import json
import configparser, os
from pymongo import MongoClient

config = configparser.RawConfigParser()
config.read('configuration.cfg')

svnroot = config.get('SVN', 'root')

svnpath = config.get('SVN', 'path')

svnusername = config.get('SVN', 'username')
svnpwd = config.get('SVN', 'pwd')

mongohost = config.get('MongoDB', 'host')
mongoport = config.getint('MongoDB', 'port')

svnclient = pysvn.Client()
svnclient.set_default_username(svnusername)
svnclient.set_default_password(svnpwd)

try:
    dirlist = svnclient.list(svnroot+svnpath,peg_revision=pysvn.Revision(pysvn.opt_revision_kind.head))
except BaseException as be:
    print("Could not connect to SVN. Execution aborted.",)
    print(be.__str__())
    sys.exit()
else:
    mongoclient = MongoClient(mongohost, mongoport)
    print("Cleaning the MongoDB collection...")
    mongodb = mongoclient.catlog
    mongodb.swagger.drop()
    for item, locked in dirlist:
        if item.kind == pysvn.node_kind.file:
            #print("Starting to process document {}".format(item.path))
            nomearquivoswagger = item.path.rpartition("/")[2]
            print("Starting to process document {}".format(nomearquivoswagger))
            swaggercontentbyte = svnclient.cat(item.path,peg_revision=pysvn.Revision(pysvn.opt_revision_kind.head))
            try:
                swaggercontentstring = swaggercontentbyte.decode("utf-8")
            except:
                print("      erro ao decode utf-8. tentando utf-8-sig")
                sys.exit(1)


            ##-------------------AJUSTES REQUERIDOS PELO SINTAXE DO SWAGGER QUE NÃO SÃO PERMITIDOS NO MONGO
            swaggercontentstring2 = swaggercontentstring.replace("$ref","ref")
            ##-------------------
            #print(swaggercontentstring2)
            try:
                swaggerjson = json.loads(swaggercontentstring2)
            except json.decoder.JSONDecodeError as jde:
                swaggercontentstring = swaggercontentbyte.decode("utf-8-sig")
                swaggercontentstring2 = swaggercontentstring.replace("$ref","ref")
                swaggerjson = json.loads(swaggercontentstring2)
            #else:
            #    print("      An encoding problem has happened when inserting Swagger information into the MongoDB collection... {}".format(getSwaggerTitle(swaggerjson)))
            #    sys.exit(1)
            swaggerjson["_id"] = nomearquivoswagger
            print("      Inserting Swagger information into the MongoDB collection...")
            try:
                result = mongodb.swagger.insert_one(swaggerjson)
            except BaseException as mongoex:
                print("            The Swagger information could not be inserted into the MongoDB collection.")
                print(mongoex.__str__())
                print()
            else:
                print("            Document _id: {}".format(nomearquivoswagger,result.inserted_id))

    mongoclient.close()