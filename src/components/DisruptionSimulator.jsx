
import { useEffect, useState } from "react";
import {
  getTopNodes,
  simulateDisruption,
} from "../services/networkApi";

function DisruptionSimulator() {
  const [criticalNodes, setCriticalNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState("");
  const [simulation, setSimulation] = useState(null);

  const [loadingNodes, setLoadingNodes] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadNodes = async () => {
      try {
        const result = await getTopNodes("betweenness", 10);

        setCriticalNodes(result.nodes);

        if (result.nodes.length > 0) {
          setSelectedNode(result.nodes[0].id);
        }
      } catch (err) {
        setError("Unable to load critical network nodes.");
      } finally {
        setLoadingNodes(false);
      }
    };

    loadNodes();
  }, []);

  const runSimulation = async () => {
    if (!selectedNode) return;

    try {
      setSimulating(true);
      setError("");
      setSimulation(null);

      const result = await simulateDisruption(selectedNode);

      setSimulation(result);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to run disruption simulation."
      );
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="risk-table-section disruption-simulator">
      <div className="risk-table-heading">
        <div>
          <h2>Disruption Simulator</h2>
          <p>
            Analyse how removing a critical network node
            affects network connectivity.
          </p>
        </div>

        <span className="live-tag">NETWORK STRESS TEST</span>
      </div>

      {loadingNodes ? (
        <p>Loading critical nodes...</p>
      ) : (
        <>
          <div className="risk-table-controls">
            <select
              value={selectedNode}
              onChange={(e) => {
                setSelectedNode(e.target.value);
                setSimulation(null);
              }}
            >
              {criticalNodes.map((node) => (
                <option key={node.id} value={node.id}>
                  {node.id} — Betweenness:{" "}
                  {Number(node.betweenness).toFixed(5)}
                </option>
              ))}
            </select>

            <button
              onClick={runSimulation}
              disabled={!selectedNode || simulating}
            >
              {simulating
                ? "Simulating..."
                : "Simulate Disruption"}
            </button>
          </div>

          {error && <p role="alert">{error}</p>}

          {simulation && (
            <div className="simulation-results">
              <h3>Simulation Results: {simulation.node_removed}</h3>

              <div className="risk-overview-grid">
                <div className="risk-overview-card total">
                  <span>Original Nodes</span>
                  <h2>
                    {simulation.original_nodes.toLocaleString()}
                  </h2>
                </div>

                <div className="risk-overview-card total">
                  <span>Remaining Nodes</span>
                  <h2>
                    {simulation.remaining_nodes.toLocaleString()}
                  </h2>
                </div>

                <div className="risk-overview-card medium">
                  <span>Original Edges</span>
                  <h2>
                    {simulation.original_edges.toLocaleString()}
                  </h2>
                </div>

                <div className="risk-overview-card medium">
                  <span>Remaining Edges</span>
                  <h2>
                    {simulation.remaining_edges.toLocaleString()}
                  </h2>
                </div>

                <div className="risk-overview-card high">
                  <span>Components After Removal</span>
                  <h2>{simulation.resulting_components}</h2>
                </div>

                <div className="risk-overview-card high">
                  <span>Nodes Outside Largest Component</span>
                  <h2>
                    {simulation.nodes_outside_largest_component}
                  </h2>
                </div>
              </div>

              <div className="risk-info-box">
                <h3>Connectivity Impact</h3>
                <p>
                  Original weakly connected components:{" "}
                  <strong>{simulation.original_components}</strong>
                </p>
                <p>
                  Largest component after removal:{" "}
                  <strong>
                    {simulation.largest_component_after_removal}
                  </strong>
                </p>
                <p>{simulation.interpretation}</p>
              </div>
            </div>
          )}
        </>
      )}

      <p className="demo-notice">
        HYPOTHETICAL NODE-REMOVAL SIMULATION — Structural
        network analysis, not an observed disruption or
        predicted probability.
      </p>
    </div>
  );
}

export default DisruptionSimulator;
