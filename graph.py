#!/usr/bin/python3
import json
import argparse
import sys
import math
# parser = argparse.ArgumentParser(
#     description="The lightning snapshot analysis tool")
# parser.add_argument("-s", "--snapshot",
#                     help="path to graph snapshot json")
# subparsers = parser.add_subparsers(title="actions")
# parser_create = subparsers.add_parser("triangles", parents=[parser],
#                                       add_help=False,
#                                       description="The triangles parser",
#                                       help="identify oppertunities to create triangels")
# parser_create.add_argument("--n", "--node", help="pubkey to target")
# parser_args = parser.parse_args()


def getGraph(path, parse):
    with open(path, 'r') as f:
        graph = json.load(f)
        return parse(graph)


def pubIndexParser(G):
    nodes = G['nodes']
    edges = G['edges']
    G = {}
    for node in nodes:
        G[node['pub_key']] = node
    for channel in edges:
        for pub in ['node1_pub', 'node2_pub']:
            if 'channels' in G[channel[pub]].keys():
                G[channel[pub]]['channels'].append(channel)
            else:
                G[channel[pub]]['channels'] = [channel]
    return G


def getPeers(G, pubkey):
    peers = []
    channels = G[pubkey]['channels']
    for pub in ['node1_pub', 'node2_pub']:
        for chan in channels:
            peer = chan[pub]
            if peer is not pubkey and peer not in peers:
                peers.append(peer)
    return peers


def getTriangles(args):
    G = getGraph(args['snapshot'], pubIndexParser)
    pubkey = args['node']
    min_triangles = int(args['min'])
    neighbors = {}
    peers = getPeers(G, pubkey)
    candidates = []
    visited = []
    for peer in peers:
        one_hops = getPeers(G, peer)
        for one_hop in one_hops:
            if one_hop not in visited and one_hop not in peers and one_hop != pubkey:
                two_hops = getPeers(G, one_hop)
                shared_edges = set(two_hops) & set(peers)
                num_triangles = len(shared_edges)
                if num_triangles >= min_triangles:
                    visited.append(one_hop)
                    candidates.append(
                        {'pubkey': one_hop, 'alias': G[one_hop]['alias'], 'num_triangles': num_triangles, 'neighbors': list(shared_edges)})
    sorted_candidates = sorted(candidates, key=lambda k: k['num_triangles'])
    return sorted_candidates


def millify(n):
    n = float(n)
    millnames = ['', 'K', 'M', 'B', 'T']
    millidx = max(0, min(len(millnames)-1,
                  int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.0f}{}'.format(n/10**(3*millidx), millnames[millidx])


args = {
    'snapshot': './graph.json',
    'node': '02ad6fb8d693dc1e4569bcedefadf5f72a931ae027dc0f0c544b34c1c6f3b9a02b',
    'min': 3
}


triangles = getTriangles(args)

print(triangles)

# with open("developer.json", "r") as read_file:
#     print("Converting JSON encoded data into Python dictionary")
#     developer = json.load(read_file)
