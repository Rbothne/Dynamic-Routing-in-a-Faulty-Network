import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
# 15 hops is max
# routers = 20, so 22 nodes (1 attacker 1 defender, 20 routers)
# each router has a unique ip, or identifier
# branches = 3 or 4 or 5
# Assume attackers are at the end of routers, multiple attackers should be one per branch at most
# No attacker on the branch should assume normal user traffic
# Assume different packet marking probability, p = 0.2, 0.4, 0.5, 0.6, 0.8 for your runs.
# Attackers send X times more packets
## TLDR: 15 hops, 22 nodes, 3->5 branches, multiple attacker scenario, probability of marking, Packet amount variance

def trimTree(T,nodeCount,branches): #generate a tree with a root, and then add a number of branches connected to that root.
    tree = list(T.nodes)
    T.add_node(0)
    for branch in range(1,branches+1):
        T.add_node(branch)
        T.add_edge(0, branch)
    tree = list(T.nodes)
    for i in range(len(tree),nodeCount+2): #Then randomly generate nodes and connections until node count is met.
        if len(tree) < nodeCount+2:
            T.add_node(i)
            startNode = random.randint(1,len(tree))
            while True:
                if startNode !=i:
                    break
                startNode = random.randint(1,len(tree))
            T.add_edge(startNode, i)
            tree = list(T.nodes)
    return T

def spawnAttackers(T,attackerC,defs): # take the list of nodes with one neighbor and set them as potential attackers. 
    potentialAttackers = [] #also be sure to return the shortest path from the attacker to the defender node.
    actualAttackers = []
    normalUser = 0
    tree = list(T.nodes)
    for node in tree:
       if len(list(T.neighbors(node))) == 1:
        potentialAttackers.append(node)
    for _ in range(attackerC):#Then randomly select N number of them as attackers. 
        attackerNode = random.randint(0,len(potentialAttackers)-1)
        actualAttackers.append(potentialAttackers[attackerNode])
        del potentialAttackers[attackerNode]
    normalUser=potentialAttackers[0] #From the remaining, select them to be a normal user.
    for attacker in actualAttackers:
        attackPath = nx.shortest_path(T,source=attacker,target=defs,weight="weight")
    return actualAttackers,attackPath,normalUser

def generateAttack(T,attackerNodes,normalUser,defender,mProb,aMult): # take in a list of attacker nodes
    distance = 0
    normalUserPackets=1
    aPackets = aMult*normalUserPackets
    packetMarks = []
    packetMark = 0
    packetEdgeMarks = []
    
    print("PATH FROM NORMAL USER ",normalUser,"TO",defender,": ",nx.shortest_path(T,source=normalUser,target=defender,weight="weight"),"LENGTH: ",nx.shortest_path_length(T, source=normalUser, target=defender, weight="weight"))
    normalUserPath = nx.shortest_path(T,source=normalUser,target=defender,weight="weight")
    #for normal users node sample
    for packet in range(normalUserPackets):
        edgeMark=defender,0,0
        for router in normalUserPath:
            failedCheck = random.random()
            if failedCheck < mProb:
                packetMark = router
                edgeMark = (router,0,0)
            else:
                if edgeMark[2] == 0:
                    edgeMark = (edgeMark[0],router,edgeMark[2])
                edgeMark= (edgeMark[0],edgeMark[1],edgeMark[2]+1)
        packetMarks.append(packetMark)
        packetEdgeMarks.append(edgeMark)
    ##for attackers node sample
    for Anode in attackerNodes:
        print("PATH FROM ATTACKER ",Anode,"TO",defender,": ",nx.shortest_path(T,source=Anode,target=defender,weight="weight"),"LENGTH: ",nx.shortest_path_length(T, source=Anode, target=defender, weight="weight"))
        attackPath = nx.shortest_path(T,source=Anode,target=defender,weight="weight")
        for packet in range(aPackets):
            edgeMark=defender,0,0
            for router in attackPath:
                failedCheck = random.random()
                if failedCheck < mProb:
                    packetMark = router
                    edgeMark = (router,0,0)
                else:
                    if edgeMark[2] == 0:
                        edgeMark = (edgeMark[0],router,edgeMark[2])
                    edgeMark= (edgeMark[0],edgeMark[1],edgeMark[2]+1)
            packetMarks.append(packetMark)
            packetEdgeMarks.append(edgeMark)

   # print (packetEdgeMarks)
    return packetMarks,packetEdgeMarks

def interpretMarks(nodeSampled,edgeSampled,attackerP):
    results = np.unique(nodeSampled, return_counts=True)
    if  np.array_equal(results[0],attackerP[::-1]) :
        accurate = 'ACCURATE'
        a = 1
    else:
        accurate ='INACCURATE'
        a = 0
    print ("-----------------------------")
    print ("node sampling says:",results[0], "with marked packet #s ",results[1],"times")
    print ("the attacker should be...",results[0][len(results[0])-1])
    print ("this result is",accurate,"in node sample with attacker path:",attackerP)
    edgeResults = []
    tupleList =[]
    G = nx.Graph()
    G.add_node(0)
    for packet in edgeSampled:
        if packet[2] == 0:
            G.add_edge(packet[0],0,distance = 0)
        else:
            G.add_edge(packet[0],packet[1],distance = packet[2])
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['distance'])
    #for u, v, a in G.edges(data=True):
        #short = nx.shortest_path_length(G, u, 0)
       # if 2 < a["distance"]:
         #   print (u,v,a)
          #  tupleList.append((u,v))
   # print(tupleList)
    #G.remove_edges_from(tupleList)
    print(sorted_edges,"SORTED EDGES")

    for edge in sorted_edges:
        if edge[0] not in edgeResults:
            edgeResults.append(edge[0])
        if edge[1] not in edgeResults:
            edgeResults.append(edge[1])
   # print (results2)
  #  print (edgeResults)
   # results2 = np.unique(packet, return_counts=True)
    
    if  np.array_equal(edgeResults,attackerP[::-1]) :
        accurate = 'ACCURATE'
        b = 1
    else:
        #print(results2[1],attackerP[::-1])
        accurate ='INACCURATE'
        b = 0

    print("\n")
    print ("edge sampling says:",edgeResults)
    print ("the attacker should be...",edgeResults[len(edgeResults)-1])
    print ("this result is",accurate,"in edge sample with attacker path:",attackerP)

    return a,b

def drawGraph(T,attackers):
    color_map = ['red' if node in attackers else 'cyan' for node in T]
    color_map[0] = 'green'
    nx.draw(T,with_labels=True,node_color=color_map)
    plt.show()

def simulate(routers,branches,attackers,mProb,aMult,defs,simulations):
    successTot = 0
    successTot2 = 0
    for _ in range(simulations):
        T = nx.Graph()
        nodeC = routers + attackers + 1 #routers + attackers + defender
        T = trimTree(T,nodeC,branches) #remove nodes higher than specified and adds nodes to meet quota
        attackerNodes = spawnAttackers(T,attackers,defs) #list of attacker nodes
        markedPackets = generateAttack(T,attackerNodes[0],attackerNodes[2],defs,mProb,aMult)
        nodeSampled = markedPackets[0]
        edgeSampled = markedPackets[1]
        success = interpretMarks(nodeSampled,edgeSampled,attackerNodes[1])
        if success[0] ==1:
            successTot +=1
        if success[1] ==1:
            successTot2 +=1

            ##DISABLE THIS TO SIMULATE MULTIPLE AT ONCE
        #drawGraph(T,attackerNodes[1])
    print(successTot,"out of",simulations, "node sample")
    print(successTot2,"out of",simulations, "edge sample")
    return successTot,successTot2,mProb,aMult

if __name__ == '__main__':
    resultsFinal = []
    hopCount = 15 #max number of hops, currently unused
    routerCount = 20 #number of routers
    branchCount = 3 #branches
    attackerCount = 2 #attackers
    #markProbability = .2 #chance to mark
    #attackerMult = 10000 #more packets attackers send relative to normal users
    defenderNode = 0 #defender spawn
    simulations = 1000
    probabiltiies = [.2,.4,.5,.6,.8]
    attackerRatio = [10,100,1000]
    for markProbability in probabiltiies:
        for attackerMult in attackerRatio:
            results = simulate(routerCount,branchCount,attackerCount,markProbability,attackerMult,defenderNode,simulations) 
            resultsFinal.append(results)
    for nodeMark, edgeMark, probabilityMark, aPackets in resultsFinal:
        print (nodeMark, edgeMark, probabilityMark, aPackets)


