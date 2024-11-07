import matplotlib.pyplot as plt
import networkx as nx
import json

#ensure working directory is set for the file location if using an interactive shell
with open(r'ND_businesses.json', "r") as file:
    data = json.load(file)

g = nx.Graph()

#construct edges
for i in data:
    if isinstance(i.get('Owner Name') or i.get('Commercial Registered Agent') or i.get('Registered Agent'), type(None)):
        continue
    else:
        g.add_edge(i.get('Company'), i.get('Owner Name') or i.get('Commercial Registered Agent') or i.get('Registered Agent'))

plt.figure(figsize=(12, 8), dpi=80)
nx.draw(g, with_labels=False, width=3, node_size=150, pos=nx.spring_layout(g, k=.1))
plt.savefig("ND_businesses_network_graph.png")
