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


#make the actual crossword by iteratively applying get_path to current crossword.
#G is the underlying graph of edges that may be used, 

def crossword(G, wordlist):
    wordlist = np.random.permutation(wordlist)
    pathdict = {}
    for v in list(G.nodes):
        G.nodes[v]['letter']='*'
        
    #for the first word, try deleting a bunch of nodes of G
    H = G.copy()
    PERCENTAGE = 0.5
    H.remove_nodes_from(random.sample(list(H.nodes),math.floor(G.order()*PERCENTAGE)))
    firstword = wordlist[0]
    path = get_path(H,firstword)
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
        path = get_path(G,word)
        i = 0
        for v in list(path.nodes):
            path.nodes[v]['letter']=word[i]
            i = i + 1
        pathdict[word]=path
        G = nx.compose(G,path)
        #print(pathlist)
        G.remove_edges_from(list(path.edges()))
        
    for path in pathdict.values():
        G = nx.compose(G,path)
        
    return G,pathdict


# a first attempt 


def simple_grid_crossword(clues, n,m):
    G = nx.grid_graph(dim=[n,m])
    H = nx.MultiDiGraph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(G.edges())
    
    G,pathdict = crossword(H,list(clues.keys()))
    #really this should catch the "no path" error.
    
    #set position as vertex name; this only makes sense for grid graph.

    pos = {}
    for v in list(G.nodes):
        pos[v]=v

    
    i=0
    cmap = plt.cm.get_cmap('Dark2')
    nodemap = plt.cm.get_cmap('Blues')
    span = len(pathdict.values())
    #fig1 = plt.subplot(1, 2, 1)
    #plt.axis("off")
    #fig2 = plt.subplot(1, 2, 2)
    #plt.axis("on")
    #fig = plt.()
    fig, axes = plt.subplots(1,2,figsize=(10,5),sharey=True)
    
    #plot graph
    
    #plt.subplot(121)
    axes[0].plot()
    #axes[0].xaxis.set_tick_params(labelbottom=True)

    #plt.axis("on")

    for word in pathdict.keys():
        #switch to graph figure 
        #ax1.plot()
        nx.draw_networkx_edges(pathdict[word],pos,edge_color = matplotlib.colors.to_hex(cmap(i/span)),ax=axes[0])
        nx.draw_networkx_edges(pathdict[word],pos,edge_color = matplotlib.colors.to_hex(cmap(i/span)),ax=axes[0])
        nx.draw_networkx_nodes(pathdict[word],pos,node_color = matplotlib.colors.to_hex(nodemap(.1)),ax=axes[0])
        i = i + 1
    plt.axis("on")
    #plt.xlim([0,m])
    #plt.ylim([0,n])
    axes[0].tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    
    #plot clues
    i = 0
    #I understand nothing
    #plt.subplot(122)
    axes[1].plot()
    plt.axis("off")
    for word in pathdict.keys():
        #switch to graph figure 
        #ax1.plot()
        
        #switch to clue figure
        #axs[1].plot()
        
        #print(list(pathdict[word].nodes()), word)
        #read from the bottom 
        
        clues[word].append(list(pathdict[word].nodes())[0])
        plt.text(0,(m-1)*i/len(pathdict),clues[word][0] + ": " + str(clues[word][1]),color = matplotlib.colors.to_hex(cmap(i/span)),fontsize=20)
        i = i + 1
    
    #need to do better to color in a non-interacting way
    
    return fig





