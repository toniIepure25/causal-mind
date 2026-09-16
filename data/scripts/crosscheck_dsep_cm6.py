import sys, itertools, random
sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
import networkx as nx
from causal_mind.causal import d_connected

def brute_d_connected(G, x, y, Z):
    # enumerate all simple undirected paths x..y, check if any is active
    Z = set(Z)
    def active(path):
        for i in range(1, len(path) - 1):
            prev, node, nxt = path[i-1], path[i], path[i+1]
            # determine collider: both edges point into node
            e1_in = (prev, node) in G.edges   # prev -> node
            e2_in = (nxt, node) in G.edges   # nxt -> node
            collider = e1_in and e2_in
            if collider:
                if not (node in Z or (set(nx.descendants(G, node)) & Z)):
                    return False
            else:
                if node in Z:
                    return False
        return True
    for path in nx.all_simple_paths(G.to_undirected(), x, y):
        if active(path):
            return True
    return False

random.seed(0)
n_tries = 0
for trial in range(300):
    n = random.randint(3, 6)
    nodes = [f"n{i}" for i in range(n)]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    order = nodes[:]
    random.shuffle(order)
    # random DAG: only add edges from earlier to later in a random topo order
    perm = order[:]
    random.shuffle(perm)
    idx = {v: i for i, v in enumerate(perm)}
    for a in nodes:
        for b in nodes:
            if a != b and idx[a] < idx[b] and random.random() < 0.4:
                G.add_edge(a, b)
    x, y = random.sample(nodes, 2)
    for r in range(0, min(n, 3) + 1):
        for Z in itertools.combinations(nodes, r):
            Zs = set(Z)
            if x in Zs or y in Zs:
                continue
            bb = d_connected(G, x, y, Zs)
            bf = brute_d_connected(G, x, y, Zs)
            n_tries += 1
            if bb != bf:
                print("MISMATCH", x, y, Z, "bayesball", bb, "brute", bf)
                print(list(G.edges))
                sys.exit(1)
print(f"d-separation cross-check OK over {n_tries} random cases")
