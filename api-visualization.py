import sys
import json
from bson.code import Code
from pymongo import MongoClient
import graphviz as gv
import configparser, os
from pymongo import MongoClient

config = configparser.RawConfigParser()
config.read('configuration.cfg')

mongohost = config.get('MongoDB', 'host')
mongoport = config.getint('MongoDB', 'port')

svggraphfile = '/Library/WebServer/Documents/grafico'

apidomainname = config.get('Graph', 'root-node-label')
graphlabel = config.get('Graph', 'title')

endnodename = "/"

def getURLs():
    mongoclient = MongoClient(mongohost, mongoport)
    mongodb = mongoclient.catlog
    reducer = Code("""function(currentObject,initialObject){
                                for(var key in currentObject.paths) {
                                    if(initialObject.results[key.trim().toLowerCase()]==undefined && currentObject._id == 'Assinatura.json'){
                                        initialObject.results[key.trim().toLowerCase()]=currentObject._id;
                                    };
                                };
                    }""")
    urls = mongodb.swagger.group(key={}, condition={}, initial={"results": {}}, reduce=reducer)
    mongoclient.close()
    return urls



urls = getURLs()

nos = {}
arestas = {}
grafos = {}

resourceanterior = ""

for url,swaggerfilename in urls[0]["results"].items():
    grafos[swaggerfilename]=""
    if resourceanterior != "":
        nos["{}".format(endnodename)] = ""
    print(url)
    resourcecandidates = url.split("/")
    resourceanterior = ""
    for r in resourcecandidates:
        if r == "": #toda url começa com "/", então o primeiro elemento do split será vazio
            resourcelabel = apidomainname
            graph = ""
            resourcekey = "{}-{}".format(apidomainname,graph)
            nos["{}".format(resourcekey)] = "{}-{}".format(graph,resourcelabel)
            print("   Node {} added to main Graph".format(resourcelabel))
        else:
            r = "/{}".format(r)
            resourcekey = "{}-{}".format(r.replace("\"","").partition("?")[0],swaggerfilename) #Se tiver "?" retorna apenas o que vem antes
            resourcelabel = r.replace("\"","").partition("?")[0]
            graph = swaggerfilename
            nos["{}".format(resourcekey)] = "{}-{}".format(graph,resourcelabel)
            print("   Node {} added to {} graph".format(resourcelabel,graph))
        if resourceanterior != "":
            if resourceanterior == "{}-{}".format(apidomainname,""):
                arestas["{}##{}".format(resourceanterior,resourcekey)] = ""
                print("   Edge {} -> {} added to main cluster".format(resourceanterior,resourcelabel))
            else:
                arestas["{}##{}".format(resourceanterior,resourcekey)] = graph
                print("   Edge {} -> {} added to cluster {}".format(resourceanterior,resourcelabel,graph))
        resourceanterior = resourcekey
    #arestas["{}##{}".format(resourceanterior,endnodename)] = ""
    print("   Edge {} -> {} added to main Graph".format(resourceanterior,endnodename))


g = gv.Digraph('G',format='png')
g.body.append('rankdir="LR"')
g.body.append('label="{}"'.format(graphlabel))
g.body.append('fontsize=16')
g.body.append('fontcolor=white')
g.body.append('fontname=Helvetica')
g.body.append("bgcolor=\"#444444\"")

g.node("{}-{}".format(apidomainname,""), label=apidomainname,style = 'filled', fillcolor = '#F05000',color='white',fontcolor='white',fontname='Helvetica')
#g.node(endnodename, style = 'filled', fillcolor = '#F05000',color='white',fontcolor='white',fontname='Helvetica')


for grafo,v in grafos.items():
    print("GRAFO {}".format(grafo))
    sg = gv.Digraph("cluster_{}".format(grafo))
    sg.body.append('style=filled')
    sg.body.append('color=\"#5C5C5C\"')
    sg.body.append('fontname=Helvetica')
    sg.body.append('label = "{}"'.format(grafo.split(".")[0]))
    sg.node_attr.update(style='filled', fillcolor='#006699',color='white',fontcolor='white',fontname='Helvetica')
    sg.edge_attr.update(arrowhead='open')
    for aresta, grafoaresta in arestas.items():
        if grafo == grafoaresta:
            sg.edge(aresta.split("##")[0], aresta.split("##")[1], style = 'solid', color = 'white')
            print("      ARESTA {} no grafo {}".format(aresta,grafo))
    for k,v in nos.items():
        if v.split("-")[0]==grafo:
            if v.split("-")[1].find("{")>0:
                sg.node(k,label=v.split("-")[1],style='dashed')
            else:
                sg.node(k,label=v.split("-")[1])

    g.subgraph(sg)

#Processa os nós adjacentes ao de inicio ou fim, ou seja, aqueles cuja aresta NAO esta totalmente dentro de um subgrafo
for aresta, grafoaresta in arestas.items():
    if grafoaresta == "":
        print("GRAFO Main")
        if aresta.partition("##")[2] == endnodename:
            g.edge(aresta.partition("##")[0],aresta.partition("##")[2], style = 'dashed', color = '#F05000')
        else:
            g.edge(aresta.partition("##")[0],aresta.partition("##")[2], style = 'solid', color = 'white')
        print("      ARESTA {}".format(aresta))


#Cluster com um unico ao inves de serem exibidos dentro do seu cluster estao no main
#...

#Declarar todos os nos para poder ajustar o estilo de cada um individualmente?
#...



g.view()

print(g)

#filename = g1.render(filename=svggraphfile)