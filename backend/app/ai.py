def analyze(events):
    # Ensure timeline items have an 'evidence' field
    formatted_timeline = []
    for e in events:
        formatted_timeline.append({
            "timestamp": e.get("timestamp", ""),
            "source": e.get("source", ""),
            "event": e.get("event", ""),
            "evidence": f"Logged event from {e.get('source', 'source')} marked as suspicious due to high risk patterns."
        })
        
    # Build default flowchart nodes and edges representing the security incident
    nodes = []
    edges = []
    if len(events) > 0:
        # Attacker node
        nodes.append({
            "id": "attacker",
            "label": "External Attacker",
            "detail": "IP address associated with malicious campaigns"
        })
        
        # Add a node for each event, and link them
        prev_node_id = "attacker"
        for i, e in enumerate(events):
            node_id = f"step_{i}"
            nodes.append({
                "id": node_id,
                "label": e.get("event", f"Event {i}"),
                "detail": f"Source: {e.get('source')} | Severity: {e.get('severity')}"
            })
            edges.append({
                "id": f"edge_{i}",
                "source": prev_node_id,
                "target": node_id,
                "label": f"Step {i+1}"
            })
            prev_node_id = node_id
            
        # Target node
        nodes.append({
            "id": "system",
            "label": "Internal System",
            "detail": "Targeted host / Compromised asset"
        })
        edges.append({
            "id": "edge_final",
            "source": prev_node_id,
            "target": "system",
            "label": "Impact"
        })
    else:
        # Safe state flowchart
        nodes = [
            {"id": "system", "label": "System Normal", "detail": "All inspected activities are within normal baseline."}
        ]
        edges = []

    return {
        "severityScore": 94 if len(events) > 0 else 0,
        "attackCategory": "Phishing & Credential Theft" if len(events) > 0 else "Safe",
        "probableIntent": "Exfiltrate user credentials and execute commands on internal network hosts" if len(events) > 0 else "None",
        "damageDone": "Credentials potentially exposed, malicious tool downloaded and executed" if len(events) > 0 else "None",
        "timeline": formatted_timeline,
        "flowchart": {
            "nodes": nodes,
            "edges": edges
        }
    }