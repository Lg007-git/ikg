import spacy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load SpaCy English model (make sure you have it installed: python -m spacy download en_core_web_sm)
nlp = spacy.load('en_core_web_sm')

# Path to your scraped tweets CSV
input_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02.csv'

# Load CSV into DataFrame
df = pd.read_csv(input_csv)

# Initialize directed graph
G = nx.DiGraph()

# Keywords for traffic issues and severity levels
traffic_keywords = ['traffic', 'congestion', 'jam', 'gridlock', 'delay', 'accident', 'roadblock', 'bottleneck']
severity_keywords = {
    'massive': 'major',
    'severe': 'major',
    'heavy': 'major',
    'minor': 'minor',
    'light': 'minor',
    'moderate': 'moderate'
}

for idx, row in df.iterrows():
    text = str(row.get('content', ''))
    doc = nlp(text)
    
    # Extract entities
    locations = [ent.text.lower() for ent in doc.ents if ent.label_ == 'LOC']
    persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    gpe = [ent.text for ent in doc.ents if ent.label_ == 'GPE']
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    events = [ent.text.lower() for ent in doc.ents if ent.label_ == 'EVENT']
    
    # Check if text contains any traffic keywords
    if any(k in text.lower() for k in traffic_keywords):
        # Determine severity if any keyword present
        severity = 'unknown'
        for word, level in severity_keywords.items():
            if word in text.lower():
                severity = level
                break
        
        # Create a unique event node id using index
        event_node = f"traffic_event_{idx}"
        
        # Add event node with attributes
        G.add_node(event_node, type='event', description=text, severity=severity)
        
        # Link event to locations
        for loc in locations:
            G.add_node(loc, type='location')
            G.add_edge(loc, event_node, relation='has_issue')
        
        # Link event to dates
        for date in dates:
            G.add_node(date, type='date')
            G.add_edge(event_node, date, relation='occurred_on')
        
        # Link event to organizations
        for org in orgs:
            G.add_node(org, type='organization')
            G.add_edge(event_node, org, relation='handled_by')
        
        # Add severity node and link to event if known
        if severity != 'unknown':
            G.add_node(severity, type='severity_level')
            G.add_edge(event_node, severity, relation='severity')
        
        reporter = row.get('user', '')
        if reporter:
            G.add_node(reporter, type='person')
            G.add_edge(reporter, event_node, relation='reported_by')

# Prepare triples list
triples = []

for u, v, data in G.edges(data=True):
    relation = data.get('relation', 'related_to')
    triples.append((u, relation, v))

# Save triples to CSV
output_file = r'D:\Scrapping\twitter_scrapping\ikg\part2\triples_output.csv'
triples_df = pd.DataFrame(triples, columns=['subject', 'predicate', 'object'])
triples_df.to_csv(output_file, index=False)

print(f"Saved {len(triples)} triples to {output_file}")

# Print basic graph stats
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# Visualization
plt.figure(figsize=(14, 10))

pos = nx.spring_layout(G, k=0.5)

# Different node colors by type
node_colors = []
for node in G.nodes(data=True):
    t = node[1].get('type')
    if t == 'location':
        node_colors.append('lightgreen')
    elif t == 'event':
        node_colors.append('orange')
    elif t == 'date':
        node_colors.append('lightblue')
    elif t == 'organization':
        node_colors.append('pink')
    elif t == 'severity_level':
        node_colors.append('red')
    else:
        node_colors.append('grey')

nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=1500, font_size=10)

edge_labels = nx.get_edge_attributes(G, 'relation')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue', font_size=9)

plt.title("Traffic Knowledge Graph with Multiple Entity Types and Relations")
plt.show()
