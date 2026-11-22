
import { useEffect, useState } from "react";
import {
  getTopNodes,
  getNodeDetails,
  simulateDisruption,
  getNodeNeighbors,
} from "../services/networkApi";

function NodeInvestigation() {
  const [criticalNodes, setCriticalNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState("");
  const [nodeDetails, setNodeDetails] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [neighbors, setNeighbors] = useState(null);

  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
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
        setLoading(false);
      }
    };

    loadNodes();
  }, []);

const investigateNode = async () => {
  if (!selectedNode) return;

  try {
    setInvestigating(true);
    setError("");
    setSimulation(null);
    setNeighbors(null);

    const [details, neighborData] = await Promise.all([
      getNodeDetails(selectedNode),
      getNodeNeighbors(selectedNode),
    ]);

    setNodeDetails(details);
    setNeighbors(neighborData);
  } catch (err) {
    setError(
      err.response?.data?.detail ||
      "Unable to retrieve node information."
    );
  } finally {
    setInvestigating(false);
  }
};

  const runSimulation = async () => {
    if (!selectedNode) return;

    try {
      setSimulating(true);
      setError("");

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

  const formatNumber = (value, digits = 4) => {
    if (value === null || value === undefined) return "N/A";

    return typeof value === "number"
      ? value.toFixed(digits)
      : value;
  };

  return (
    <div className="risk-table-section">
      <div className="risk-table-heading">
        <div>
          <h2>Node Investigation</h2>
          <p>
            Investigate critical nodes using real AnonNet
            network data and centrality metrics.
          </p>
        </div>

        <span className="live-tag">NETWORK INTELLIGENCE</span>
      </div>

      {loading ? (
        <p>Loading critical nodes...</p>
      ) : (
        <>
          <div className="risk-table-controls">
            <select
              value={selectedNode}
              onChange={(e) => {
                setSelectedNode(e.target.value);
                setNodeDetails(null);
                setSimulation(null);
		setNeighbors(null);
                setError("");
              }}
            >
              {criticalNodes.map((node) => (
                <option key={node.id} value={node.id}>
                  {node.id} — Betweenness:{" "}
                  {formatNumber(node.betweenness, 5)}
                </option>
              ))}
            </select>

            <button
              onClick={investigateNode}
              disabled={!selectedNode || investigating}
            >
              {investigating ? "Investigating..." : "Investigate Node"}
            </button>

            <button
              onClick={runSimulation}
              disabled={!selectedNode || simulating}
            >
              {simulating ? "Simulating..." : "Run Stress Test"}
            </button>
          </div>

          {error && <p role="alert">{error}</p>}

          {nodeDetails && (
            <div className="simulation-results">
              <h3>Node Profile: {nodeDetails.id}</h3>

              <div className="risk-overview-grid">
                <div className="risk-overview-card total">
                  <span>Location</span>
                  <h2>{nodeDetails.location || "Unknown"}</h2>
                </div>

                <div className="risk-overview-card total">
                  <span>Products</span>
                  <h2>{nodeDetails.products || "Unknown"}</h2>
                </div>

                <div className="risk-overview-card medium">
                  <span>In-degree</span>
                  <h2>{formatNumber(nodeDetails.in_degree, 0)}</h2>
                </div>

                <div className="risk-overview-card medium">
                  <span>Out-degree</span>
                  <h2>{formatNumber(nodeDetails.out_degree, 0)}</h2>
                </div>

                <div className="risk-overview-card high">
                  <span>Total Degree</span>
                  <h2>{formatNumber(nodeDetails.total_degree, 0)}</h2>
                </div>

                <div className="risk-overview-card high">
                  <span>Betweenness</span>
                  <h2>{formatNumber(nodeDetails.betweenness, 5)}</h2>
                </div>

                <div className="risk-overview-card total">
                  <span>PageRank</span>
                  <h2>{formatNumber(nodeDetails.pagerank, 6)}</h2>
                </div>
              </div>

              <p className="demo-notice">
                Centrality values describe structural importance
                in the anonymised network. They do not establish
                the node's real-world business role or disruption
                probability.
              </p>
            </div>
          )}
	

{neighbors && (
  <div className="simulation-results">
    <h3>Network Neighbour Explorer</h3>

    <p>
      Direct connections for node{" "}
      <strong>{neighbors.node_id}</strong>
    </p>

    <div className="risk-overview-grid">
      <div className="risk-overview-card total">
        <span>Incoming Connections</span>
        <h2>{neighbors.incoming_count}</h2>
      </div>

      <div className="risk-overview-card medium">
        <span>Outgoing Connections</span>
        <h2>{neighbors.outgoing_count}</h2>
      </div>
    </div>

    <div className="risk-info-box">
      <h3>Incoming Neighbours</h3>
      <p>
        Nodes with edges pointing towards{" "}
        <strong>{neighbors.node_id}</strong>
      </p>

      {neighbors.incoming_neighbors.length === 0 ? (
        <p>No incoming neighbours found.</p>
      ) : (
        <div className="risk-table-container">
          <table>
            <thead>
              <tr>
                <th>Node ID</th>
                <th>Location</th>
                <th>Products</th>
              </tr>
            </thead>
            <tbody>
              {neighbors.incoming_neighbors.map((node) => (
                <tr key={node.id}>
                  <td>{node.id}</td>
                  <td>{node.location || "Unknown"}</td>
                  <td>{node.products || "Unknown"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>

    <div className="risk-info-box">
      <h3>Outgoing Neighbours</h3>
      <p>
        Nodes that{" "}
        <strong>{neighbors.node_id}</strong>{" "}
        has edges pointing towards
      </p>

      {neighbors.outgoing_neighbors.length === 0 ? (
        <p>No outgoing neighbours found.</p>
      ) : (
        <div className="risk-table-container">
          <table>
            <thead>
              <tr>
                <th>Node ID</th>
                <th>Location</th>
                <th>Products</th>
              </tr>
            </thead>
            <tbody>
              {neighbors.outgoing_neighbors.map((node) => (
                <tr key={node.id}>
                  <td>{node.id}</td>
                  <td>{node.location || "Unknown"}</td>
                  <td>{node.products || "Unknown"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  </div>
)}


          {simulation && (
            <div className="risk-info-box">
              <h3>Stress Test: {simulation.node_removed}</h3>
              <p>
                Remaining nodes:{" "}
                <strong>{simulation.remaining_nodes.toLocaleString()}</strong>
              </p>
              <p>
                Remaining edges:{" "}
                <strong>{simulation.remaining_edges.toLocaleString()}</strong>
              </p>
              <p>
                Resulting weakly connected components:{" "}
                <strong>{simulation.resulting_components}</strong>
              </p>
              <p>
                Nodes outside largest component:{" "}
                <strong>
                  {simulation.nodes_outside_largest_component}
                </strong>
              </p>
              <p>{simulation.interpretation}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default NodeInvestigation;
