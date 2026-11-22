import NodeInvestigation from "../components/NodeInvestigation";
import VisualNetworkExplorer from "../components/VisualNetworkExplorer";
import { initialNodes, initialEdges } from "../data/mockGraph";
import { getDownstreamNodeIds } from "../components/NetworkGraph";
import { useState, useEffect } from "react";
import {
  getNetworkSummary,
  getTopNodes,
} from "../services/networkApi";
import {
  AlertTriangle,
  ShieldAlert,
  Activity,
  TrendingUp,
  Search,
} from "lucide-react";
import DisruptionSimulator from "../components/DisruptionSimulator";

function RiskMonitoring() {
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [networkSummary, setNetworkSummary] = useState(null);
  const [criticalNodes, setCriticalNodes] = useState([]);
  const [networkLoading, setNetworkLoading] = useState(true);
  const [networkError, setNetworkError] = useState("");

  useEffect(() => {
    const fetchNetworkData = async () => {
      try {
        setNetworkLoading(true);
        setNetworkError("");

        const [summary, topNodes] = await Promise.all([
          getNetworkSummary(),
          getTopNodes("betweenness", 5),
        ]);

        setNetworkSummary(summary);
        setCriticalNodes(topNodes.nodes);
      } catch (error) {
        console.error("Network API error:", error);
        setNetworkError(
          "Unable to load live network intelligence. Check whether the backend is running."
        );
      } finally {
        setNetworkLoading(false);
      }
    };

    fetchNetworkData();
  }, []);

  const riskEntities = [
    {
      id: 1,
      name: "Rotterdam Port",
      type: "Port",
      location: "Netherlands",
      score: 92,
      risk: "High",
      disruption: "Port Congestion",
    },
    {
      id: 2,
      name: "European Supplier",
      type: "Supplier",
      location: "Germany",
      score: 65,
      risk: "Medium",
      disruption: "Shipping Delays",
    },
    {
      id: 3,
      name: "Electronics Factory",
      type: "Manufacturer",
      location: "Germany",
      score: 85,
      risk: "High",
      disruption: "Component Shortage",
    },
    {
      id: 4,
      name: "Component Supplier",
      type: "Supplier",
      location: "China",
      score: 25,
      risk: "Low",
      disruption: "No Active Disruption",
    },
    {
      id: 5,
      name: "North American Factory",
      type: "Manufacturer",
      location: "USA",
      score: 58,
      risk: "Medium",
      disruption: "Transport Delays",
    },
    {
      id: 6,
      name: "Hamburg Port",
      type: "Port",
      location: "Germany",
      score: 88,
      risk: "High",
      disruption: "Weather Disruption",
    },
  ];
  const highRiskCount = riskEntities.filter(
  (entity) => entity.risk === "High"
).length;

const mediumRiskCount = riskEntities.filter(
  (entity) => entity.risk === "Medium"
).length;

const lowRiskCount = riskEntities.filter(
  (entity) => entity.risk === "Low"
).length;

const totalMonitored = riskEntities.length;
  const selectedGraphNode = selectedEntity
  ? initialNodes.find((node) => node.data.label === selectedEntity.name)
  : null;

const downstreamNodeIds = selectedGraphNode
  ? getDownstreamNodeIds(selectedGraphNode.id, initialEdges)
  : [];

const downstreamNodes = initialNodes.filter((node) =>
  downstreamNodeIds.includes(node.id)
);

const downstreamCountries = [
  ...new Set(downstreamNodes.map((node) => node.data.country)),
];

  const filteredEntities = riskEntities.filter((entity) => {
    const search = searchTerm.trim().toLowerCase();

const matchesSearch =
  entity.name.toLowerCase().includes(search) ||
  entity.location.toLowerCase().includes(search) ||
  entity.type.toLowerCase().includes(search) ||
  entity.risk.toLowerCase().includes(search) ||
  `${entity.risk} risk`.toLowerCase().includes(search) ||
  entity.disruption.toLowerCase().includes(search);
    const matchesRisk =
      riskFilter === "All" || entity.risk?.trim().toLowerCase() === riskFilter.trim().toLowerCase();

    return matchesSearch && matchesRisk;
  });

  const sortedEntities = [...filteredEntities].sort(
  (a, b) => b.score - a.score
);
const filteredCount = filteredEntities.length;

const filteredPercentage = Math.round(
  (filteredCount / riskEntities.length) * 100
);

  return (
    <div className="risk-monitoring-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">ANALYTICS / RISK MONITORING</p>
          <h1>Risk Monitoring</h1>
          <p className="subtitle">
            Monitor supply-chain vulnerabilities and identify
            high-risk entities across your network.
          </p>
        </div>
      </div>

      <div className="risk-overview-grid">

  <div className="risk-overview-card high">
    <div className="risk-card-top">
      <span>High Risk</span>
      <ShieldAlert size={20} />
    </div>
    <h2>{highRiskCount}</h2>
    <p>Entities requiring immediate attention</p>
  </div>

  <div className="risk-overview-card medium">
    <div className="risk-card-top">
      <span>Medium Risk</span>
      <AlertTriangle size={20} />
    </div>
    <h2>{mediumRiskCount}</h2>
    <p>Entities requiring close monitoring</p>
  </div>

  <div className="risk-overview-card low">
    <div className="risk-card-top">
      <span>Low Risk</span>
      <Activity size={20} />
    </div>
    <h2>{lowRiskCount}</h2>
    <p>Entities operating with lower risk</p>
  </div>

  <div className="risk-overview-card total">
    <div className="risk-card-top">
      <span>Total Monitored</span>
      <TrendingUp size={20} />
    </div>
    <h2>{totalMonitored}</h2>
    <p>Entities currently being monitored</p>
  </div>

</div>
<div className="risk-table-section">
  <div className="risk-table-heading">
    <div>
      <h2>Live Network Intelligence</h2>
      <p>Real structural metrics from the AnonNet supply-chain network.</p>
    </div>
    <span className="live-tag">LIVE API DATA</span>
  </div>

  {networkLoading ? (
    <p>Loading network intelligence...</p>
  ) : networkError ? (
    <p>{networkError}</p>
  ) : networkSummary ? (
    <>
      <div className="risk-overview-grid">
        <div className="risk-overview-card total">
          <div className="risk-card-top">
            <span>Network Nodes</span>
            <Activity size={20} />
          </div>
          <h2>{networkSummary.total_nodes.toLocaleString()}</h2>
          <p>Anonymised network entities</p>
        </div>

        <div className="risk-overview-card total">
          <div className="risk-card-top">
            <span>Network Connections</span>
            <TrendingUp size={20} />
          </div>
          <h2>{networkSummary.total_edges.toLocaleString()}</h2>
          <p>Directed connections</p>
        </div>

        <div className="risk-overview-card medium">
          <div className="risk-card-top">
            <span>Average In-degree</span>
            <Activity size={20} />
          </div>
          <h2>{networkSummary.average_in_degree}</h2>
          <p>Average incoming connections</p>
        </div>

        <div className="risk-overview-card medium">
          <div className="risk-card-top">
            <span>Average Out-degree</span>
            <Activity size={20} />
          </div>
          <h2>{networkSummary.average_out_degree}</h2>
          <p>Average outgoing connections</p>
        </div>
      </div>

      <h3>Top 5 Structurally Critical Nodes</h3>
      <p>Ranked by betweenness centrality.</p>

      <div className="risk-table-wrapper">
        <table className="risk-table">
          <thead>
            <tr>
              <th>Node ID</th>
              <th>Location</th>
              <th>In-degree</th>
              <th>Out-degree</th>
              <th>Betweenness</th>
            </tr>
          </thead>
          <tbody>
            {criticalNodes.map((node) => (
              <tr key={node.id}>
                <td className="entity-name">{node.id}</td>
                <td>{node.location || "Unknown"}</td>
                <td>{node.in_degree}</td>
                <td>{node.out_degree}</td>
                <td>{Number(node.betweenness).toFixed(6)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p>
        Weakly connected components:{" "}
        <strong>{networkSummary.weakly_connected_components}</strong>
        {" · "}
        Largest component:{" "}
        <strong>{networkSummary.largest_component_size}</strong>
        {" · "}
        Self-loops: <strong>{networkSummary.self_loops}</strong>
      </p>
    </>
  ) : null}
</div>
      
<div className="risk-table-section">

  <div className="risk-table-heading">
    <div>
      <h2>Risk Assessment</h2>
      <p>Identify and investigate vulnerable supply-chain entities.</p>
    </div>
    <span className="live-tag">RISK REGISTER</span>
  </div>
  <div className="risk-filter-summary">
  <div>
    <strong>{filteredCount}</strong>
    <span>
      {riskFilter === "All" ? "Total matching entities" : `${riskFilter} risk entities`}
    </span>
  </div>

  <div className="risk-filter-progress">
    <div className="risk-filter-progress-track">
      <div
        className="risk-filter-progress-fill"
        style={{ width: `${filteredPercentage}%` }}
      ></div>
    </div>
    <span>{filteredPercentage}% of monitored entities</span>
  </div>
</div>

  <div className="risk-table-controls">
    <div className="risk-search">
      <Search size={18} />
      <input
        type="text"
        placeholder="Search entity or location..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
    </div>

    <select
      value={riskFilter}
      onChange={(e) => setRiskFilter(e.target.value)}
    >
      <option value="All">All Risks</option>
      <option value="High">High Risk</option>
      <option value="Medium">Medium Risk</option>
      <option value="Low">Low Risk</option>
    </select>
  </div>

  <div className="risk-table-wrapper">
    <table className="risk-table">
      <thead>
        <tr>
          <th>Entity</th>
          <th>Type</th>
          <th>Location</th>
          <th>Risk Score</th>
          <th>Risk Level</th>
          <th>Disruption</th>
        </tr>
      </thead>

     
<tbody>
  {filteredEntities.length > 0 ? (
    sortedEntities.map((entity) => (
      <tr
        key={entity.id}
        className="clickable-risk-row"
        onClick={() => setSelectedEntity(entity)}
      >
        <td className="entity-name">{entity.name}</td>

        <td>{entity.type}</td>

        <td>{entity.location}</td>

        <td>
          <div className="risk-score-cell">
            <strong>{entity.score}/100</strong>
            <div className="risk-score-track">
      <div
        className={`risk-score-fill ${entity.risk.toLowerCase()}`}
        style={{ width: `${entity.score}%` }}
              ></div>
            </div>
          </div>
        </td>

        <td>
          <span className={`risk-badge ${entity.risk.toLowerCase()}`}>
            {entity.risk}
          </span>
        </td>

        <td>{entity.disruption}</td>
      </tr>
    ))
  ) : (
    <tr>
      <td colSpan="6" className="empty-risk">
        No matching entities found.
      </td>
    </tr>
  )}
</tbody>

    </table>
  </div>

  <div className="risk-table-footer">
    Showing {filteredEntities.length} of {riskEntities.length} entities
  </div>

{selectedEntity && (
  <div className="risk-details-panel">

    <div className="risk-details-header">
      <div>
        <p className="eyebrow">ENTITY / RISK INVESTIGATION</p>
        <h2>{selectedEntity.name}</h2>
        <p>{selectedEntity.type} · {selectedEntity.location}</p>
      </div>

      <button
        className="close-risk-details"
        onClick={() => setSelectedEntity(null)}
      >
        ✕
      </button>
    </div>

    <div className="risk-details-content">

      <div className="risk-score-box">
        <span>Risk Score</span>
        <h2>{selectedEntity.score}<small>/100</small></h2>
        <span className={`risk-badge ${selectedEntity.risk.toLowerCase()}`}>
          {selectedEntity.risk} Risk
        </span>
      </div>

      <div className="risk-info-box">
        <span>Reported Disruption</span>
        <h3>{selectedEntity.disruption}</h3>
        <p>
          This entity has been flagged for supply-chain risk monitoring.
        </p>
      </div>

      <div className="risk-info-box">
        <span>Recommended Mitigation</span>
        <h3>
          {selectedEntity.risk === "High"
            ? "Activate alternative suppliers"
            : selectedEntity.risk === "Medium"
            ? "Monitor supplier performance"
            : "Continue routine monitoring"}
        </h3>
        <p>
          Suggested action based on the current demo risk classification.
        </p>
      </div>

    </div>

<div className="downstream-impact-section">
  <div className="downstream-impact-heading">
    <div>
      <span>NETWORK INTELLIGENCE</span>
      <h3>Downstream Impact Analysis</h3>
      <p>Connected entities potentially affected by this disruption.</p>
    </div>

    <span className="impact-count-badge">
      {downstreamNodes.length} affected
    </span>
  </div>

  {selectedGraphNode ? (
    downstreamNodes.length > 0 ? (
      <>
        <div className="downstream-impact-summary">
          <div>
            <strong>{downstreamNodes.length}</strong>
            <span>Affected entities</span>
          </div>
          <div>
            <strong>{downstreamCountries.length}</strong>
            <span>Countries</span>
          </div>
        </div>

        <div className="downstream-entity-list">
          {downstreamNodes.map((node) => (
            <div className="downstream-entity" key={node.id}>
              <div>
                <strong>{node.data.label}</strong>
                <span>{node.data.type} · {node.data.country}</span>
              </div>

              <span className={`risk-badge ${node.data.risk.toLowerCase()}`}>
                {node.data.risk}
              </span>
            </div>
          ))}
        </div>
      </>
    ) : (
      <p>No downstream entities are connected to this node.</p>
    )
  ) : (
    <p>This entity is not yet included in the current supply network graph.</p>
  )}
</div>


  </div>
)}


</div>
<DisruptionSimulator />
<NodeInvestigation />
<VisualNetworkExplorer />

    </div>
  );
}

export default RiskMonitoring;
