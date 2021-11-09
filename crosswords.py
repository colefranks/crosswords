#approach with grid. 

import networkx as nx
import numpy as np
import random
import math
import scipy

from networkx.algorithms import tournament
import matplotlib.pyplot as plt

#helper function 

def letter_filter(G, filterlist):
    kept = []
    for v in G.nodes():
        if G.nodes[v]['letter'] in filterlist[v[1]]:
            kept.append(v)
    return kept


#greedily chooses next path for the word. Just requires that the given digraph have no directed cycles.

def get_path(labeled_graph,word):

    GRAPHSIZE = labeled_graph.order()
    WORDLENGTH=len(word)
    path = nx.MultiDiGraph()
    nx.add_path(path,range(WORDLENGTH))
    word_dict = word_to_dict(word)
    nx.set_node_attributes(path, word_dict, 'letter')


    product_graph = nx.tensor_product(labeled_graph,path)

    # removes the vertices where letter doesn't match
    
    for v in list(product_graph.nodes):
        #print(B.nodes[v]['letter'][0])
        if not (product_graph.nodes[v]['letter'][0]==product_graph.nodes[v]['letter'][1] or product_graph.nodes[v]['letter'][0]=='*'):
            #print(B.nodes[v]['letter'][0]), print(B.nodes[v]['letter'][1])
            product_graph.remove_node(v)

            
    #weight the edges

    for e in list(product_graph.edges):
        product_graph.edges[e]['weight']=0
        if product_graph.nodes[e[0]]['letter'][0]=='*':
            product_graph.edges[e]['weight']= product_graph.edges[e]['weight']+1
        if product_graph.nodes[e[1]]['letter'][0]=='*':
            product_graph.edges[e]['weight']= product_graph.edges[e]['weight']+1

    #add source and sink
    
    product_graph.add_node('s')
    product_graph.add_node('t')
    for i in list(labeled_graph.nodes):
        if (i,0) in list(product_graph.nodes):
            product_graph.add_edge('s',(i,0))
        if (i,WORDLENGTH-1) in list(product_graph.nodes):
            product_graph.add_edge((i,WORDLENGTH-1),'t')




    dijkstra = nx.dijkstra_path(product_graph, 's', 't')
    original_path=[]
    for v in dijkstra:
        if v!='s' and v!='t':
            original_path.append(v[0])
    #make it into an actual path
    #print(original_path)
    P = nx.MultiDiGraph()
    nx.add_path(P,original_path)
    #gotta get the letters out

    return P




#F should be an acyclic multidigraph (the underlying graph)
#wordlist a list of strings (the answers)

def crossword(F, wordlist,max_iter=20):
    nopath=True
    for v in list(F.nodes):
        F.nodes[v]['letter']='*'
    iter=0
    while nopath and iter < max_iter:
        iter+=1
        G = F.copy()
        wordlist = np.random.permutation(wordlist)
        pathdict = {}
        
        #for the first word, try deleting a bunch of nodes of G
        H = G.copy()
        PERCENTAGE = 0.5
        H.remove_nodes_from(random.sample(list(H.nodes),math.floor(G.order()*PERCENTAGE)))
        firstword = wordlist[0]
        try: 
            path = get_path(H,firstword)
        except nx.NetworkXNoPath:
            nopath=True
            continue  
        i = 0
        for v in list(path.nodes):
            path.nodes[v]['letter']=firstword[i]
            i = i + 1
        pathdict[firstword]=path
        G = nx.compose(G,path)
        #print(pathlist)
        G.remove_edges_from(list(path.edges()))
        wordlist = wordlist[1:]

    
        for word in wordlist:
            #get the path. if there is none, just start over
            #when we start over we need to copy.
            #could have some "dropout" to enforce randomness.
            try: 
                path = get_path(G,word)
            except nx.NetworkXNoPath:
                nopath=True
                break
            nopath=False
            i = 0
            for v in list(path.nodes):
                path.nodes[v]['letter']=word[i]
                i = i + 1
            pathdict[word]=path
            G = nx.compose(G,path)
            #print(pathlist)
            G.remove_edges_from(list(path.edges()))
        
        if nopath:
            continue
            
        for path in pathdict.values():
            G = nx.compose(G,path)
        
    return G,pathdict

# a first attempt using grid
#clues is a word:clue dictionary


def simple_grid_crossword(clues, n,m):
    G = nx.grid_graph(dim=[n,m])
    H = nx.MultiDiGraph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(G.edges())
    
    G,pathdict = crossword(H,list(clues.keys()))
    
    #set position as vertex name; this only makes sense for grid graph.

    pos = {}
    for v in list(G.nodes):
        pos[v]=v
    
    #could also do spring layout
    #pos = nx.spring_layout(G)
    #print(pos)
    
    
    i=0
    cmap = plt.cm.get_cmap('Dark2')
    nodemap = plt.cm.get_cmap('Blues')
    span = len(pathdict.values())

    fig, axes = plt.subplots(1,2,figsize=(10,5),sharey=True)
    

    axes[0].plot()
    
    #plot the graph 

    for word in pathdict.keys():

        nx.draw_networkx_edges(pathdict[word],pos,edge_color = matplotlib.colors.to_hex(cmap(i/span)),ax=axes[0])
        nx.draw_networkx_edges(pathdict[word],pos,edge_color = matplotlib.colors.to_hex(cmap(i/span)),ax=axes[0])
        nx.draw_networkx_nodes(pathdict[word],pos,node_color = matplotlib.colors.to_hex(nodemap(.1)),ax=axes[0])
        i = i + 1
    plt.axis("on")
    axes[0].tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    
    #plot clues
    i = 0

    axes[1].plot()
    plt.axis("off")
    for word in pathdict.keys():
        
        clues[word].append(list(pathdict[word].nodes())[0])
        plt.text(0,(m-1)*i/len(pathdict),clues[word][0] + ": " + str(clues[word][1]),color = matplotlib.colors.to_hex(cmap(i/span)),fontsize=20)
        i = i + 1
    
    #need to do better to color in a non-interacting way
    
    return fig





