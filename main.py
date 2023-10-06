import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

def trim_tree(T, node_count, branches):
    tree = list(T.nodes)
    T.add_node(0)
    
    for branch in range(1, branches + 1):
        T.add_node(branch)
        T.add_edge(0, branch)
    
    tree = list(T.nodes)
    
    while len(tree) < node_count + 2:
        i = len(tree)
        T.add_node(i)
        start_node = random.randint(1, len(tree))
        
        while True:
            if start_node != i:
                break
            start_node = random.randint(1, len(tree))
        
        T.add_edge(start_node, i)
        tree = list(T.nodes)
    
    return T

def generate_attack(T, attacker_nodes, normal_user, defender, m_prob, a_mult):
    distance = 0
    normal_user_packets = 1
    a_packets = a_mult * normal_user_packets
    packet_marks = []
    packet_mark = 0
    packet_edge_marks = []

    print("PATH FROM NORMAL USER", normal_user, "TO", defender, ":", nx.shortest_path(T, source=normal_user, target=defender, weight="weight"), "LENGTH:", nx.shortest_path_length(T, source=normal_user, target=defender, weight="weight"))
    normal_user_path = nx.shortest_path(T, source=normal_user, target=defender, weight="weight")
    
    for packet in range(normal_user_packets):
        edge_mark = defender, 0, 0
        for router in normal_user_path:
            failed_check = random.random()
            if failed_check < m_prob:
                packet_mark = router
                edge_mark = (router, 0, 0)
            else:
                if edge_mark[2] == 0:
                    edge_mark = (edge_mark[0], router, edge_mark[2])
                edge_mark = (edge_mark[0], edge_mark[1], edge_mark[2] + 1)
        packet_marks.append(packet_mark)
        packet_edge_marks.append(edge_mark)

    for Anode in attacker_nodes:
        print("PATH FROM ATTACKER", Anode, "TO", defender, ":", nx.shortest_path(T, source=Anode, target=defender, weight="weight"), "LENGTH:", nx.shortest_path_length(T, source=Anode, target=defender, weight="weight"))
        attack_path = nx.shortest_path(T, source=Anode, target=defender, weight="weight")
        for packet in range(a_packets):
            edge_mark = defender, 0, 0
            for router in attack_path:
                failed_check = random.random()
                if failed_check < m_prob:
                    packet_mark = router
                    edge_mark = (router, 0, 0)
                else:
                    if edge_mark[2] == 0:
                        edge_mark = (edge_mark[0], router, edge_mark[2])
                    edge_mark = (edge_mark[0], edge_mark[1], edge_mark[2] + 1)
            packet_marks.append(packet_mark)
            packet_edge_marks.append(edge_mark)

    return packet_marks, packet_edge_marks

def interpret_marks(node_sampled, edge_sampled, attacker_path):
    results = np.unique(node_sampled, return_counts=True)
    
    if np.array_equal(results[0], attacker_path[::-1]):
        accurate = 'ACCURATE'
        a = 1
    else:
        accurate = 'INACCURATE'
        a = 0
    
    print("-----------------------------")
    print("node sampling says:", results[0], "with marked packet #s", results[1], "times")
    print("the attacker should be...", results[0][len(results[0]) - 1])
    print("this result is", accurate, "in node sample with attacker path:", attacker_path)
    
    edge_results = []
    tuple_list = []
    G = nx.Graph()
    G.add_node(0)
    
    for packet in edge_sampled:
        if packet[2] == 0:
            G.add_edge(packet[0], 0, distance=0)
        else:
            G.add_edge(packet[0], packet[1], distance=packet[2])
    
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['distance'])
    
    for edge in sorted_edges:
        if edge[0] not in edge_results:
            edge_results.append(edge[0])
        if edge[1] not in edge_results:
            edge_results.append(edge[1])
    
    if np.array_equal(edge_results, attacker_path[::-1]):
        accurate = 'ACCURATE'
        b = 1
    else:
        accurate = 'INACCURATE'
        b = 0

    print("\n")
    print("edge sampling says:", edge_results)
    print("the attacker should be...", edge_results[len(edge_results) - 1])
    print("this result is", accurate, "in edge sample with attacker path:", attacker_path)

    return a, b

def draw_graph(T, attackers):
    color_map = ['red' if node in attackers else 'cyan' for node in T]
    color_map[0] = 'green'
    nx.draw(T, with_labels=True, node_color=color_map)
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
    results_final = []
    hop_count = 15
    router_count = 20
    branch_count = 3
    attacker_count = 2
    defender_node = 0
    simulations = 1000
    probabilities = [0.2, 0.4, 0.5, 0.6, 0.8]
    attacker_ratios = [10, 100, 1000]

    for mark_probability in probabilities:
        for attacker_mult in attacker_ratios:
            results = simulate(router_count, branch_count, attacker_count, mark_probability, attacker_mult, defender_node, simulations)
            results_final.append(results)

    for node_mark, edge_mark, probability_mark, a_packets in results_final:
        print(node_mark, edge_mark, probability_mark, a_packets)