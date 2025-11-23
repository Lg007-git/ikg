from pyvis.network import Network
import networkx as nx

from triples_extrat import G

# Suppose G is your NetworkX graph already built
# (with nodes and edges and maybe attributes)

def visualize_graph_pyvis(G, output_html="traffic_graph.html"):
    net = Network(height="750px", width="100%", notebook=False)
    
    # Optionally: add some physics / layout options
    net.force_atlas_2based()  # enable nicer force-based layout
    
    net.from_nx(G)  # import nodes and edges

    # Add titles or tooltips if available
    for node, attrs in G.nodes(data=True):
        title = attrs.get('description', '')
        net.get_node(node)['title'] = title
        # You can set group, color, size etc. from attrs if present.

    net.show(output_html)
    print(f"Graph visualization saved to {output_html}")

# Example usage
visualize_graph_pyvis(G, output_html="traffic_kg.html")
