import networkx as nx
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import Sampler
import matplotlib.pyplot as plt

def create_graph():
    """Create a simple graph for coloring."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    return G

def quantum_graph_coloring(graph, num_colors):
    """Implement quantum circuit for graph coloring."""
    num_nodes = len(graph.nodes)
    
    color_qubits = QuantumRegister(num_nodes * 2, 'color')
    result_qubits = QuantumRegister(num_nodes, 'result')
    cr = ClassicalRegister(num_nodes * 2 + num_nodes, 'measure')
    circuit = QuantumCircuit(color_qubits, result_qubits, cr)

    for i in range(num_nodes * 2):
        circuit.h(color_qubits[i])

    for edge in graph.edges():
        i, j = edge
        circuit.cx(color_qubits[2*i], result_qubits[i])
        circuit.cx(color_qubits[2*j], result_qubits[j])

    circuit.measure(color_qubits, cr[:num_nodes*2])
    circuit.measure(result_qubits, cr[num_nodes*2:])

    return circuit

def run_quantum_circuit(circuit, shots=1000):
    """Execute the quantum circuit and return results."""
    sampler = Sampler()
    job = sampler.run(circuit, shots=shots)
    result = job.result()
    counts = result.quasi_dists[0].binary_probabilities()
    return {format(int(k), '0' + str(len(circuit.clbits)) + 'b'): v for k, v in counts.items()}

def interpret_results(counts, num_nodes):
    """Interpret the measurement results."""
    valid_colorings = {}
    for outcome, probability in counts.items():
        color_bits = outcome[:num_nodes*2]
        result_bits = outcome[num_nodes*2:]
        coloring = tuple(int(color_bits[i:i+2], 2) for i in range(0, len(color_bits), 2))
        if '1' not in result_bits:
            valid_colorings[coloring] = int(probability * 1000)
    return valid_colorings

def visualize_coloring(G, coloring):
    """Visualize the graph with the given coloring."""
    color_map = ['red', 'green', 'blue', 'yellow']
    node_colors = [color_map[c] for c in coloring]
    plt.figure(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_color=node_colors, node_size=500, font_size=16, font_weight='bold')
    plt.title(f"Graph Coloring: {coloring}")
    plt.show()

def main():
    G = create_graph()
    num_colors = 3

    circuit = quantum_graph_coloring(G, num_colors)
    counts = run_quantum_circuit(circuit)

    valid_colorings = interpret_results(counts, len(G.nodes))

    print("Valid colorings found:")
    for coloring, count in valid_colorings.items():
        print(f"Coloring {coloring}: {count} occurrences")
        visualize_coloring(G, coloring)

    # Visualize all results
    plt.figure(figsize=(10, 6))
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels = [f"{k[:len(G.nodes)*2]}" for k, _ in sorted_counts[:10]]  # Show only color bits for top 10
    values = [v for _, v in sorted_counts[:10]]
    plt.bar(range(len(values)), values)
    plt.xticks(range(len(values)), labels, rotation=45, ha='right')
    plt.title("Top 10 Measurement Outcomes (Color Bits Only)")
    plt.xlabel("Measured State (Color Bits)")
    plt.ylabel("Probability")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
