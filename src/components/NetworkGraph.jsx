
import { Search } from "lucide-react";
import { useState } from "react";

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { initialNodes, initialEdges } from "../data/mockGraph";
import CustomNode from "./CustomNode";

// Register custom node types
const nodeTypes = {
  custom: CustomNode,
};
function getDownstreamNodeIds(startId, edges) {
  const visited = new Set();
  const queue = [startId];

  while (queue.length > 0) {
    const currentId = queue.shift();

    const downstreamEdges = edges.filter(
      (edge) => edge.source === currentId
    );

    downstreamEdges.forEach((edge) => {
      if (!visited.has(edge.target)) {
        visited.add(edge.target);
        queue.push(edge.target);
      }
    });
  }

  return [...visited];
}

function NetworkGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialNodes.map((node) => ({
      ...node,
      type: "custom",
    }))
  );

  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [impactedNodeIds, setImpactedNodeIds] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [selectedNode, setSelectedNode] = useState(null);
  const impactedNodes = nodes.filter((node) =>
  impactedNodeIds.includes(node.id)
);

const impactedCountries = [
  ...new Set(impactedNodes.map((node) => node.data.country)),
];

const highRiskCount = impactedNodes.filter(
  (node) => node.data.risk === "High"
).length;

const mediumRiskCount = impactedNodes.filter(
  (node) => node.data.risk === "Medium"
).length;

const lowRiskCount = impactedNodes.filter(
  (node) => node.data.risk === "Low"
).length;
  const visibleNodes = nodes.filter((node) => {
  const matchesSearch =
    node.data.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.data.country.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.data.type.toLowerCase().includes(searchTerm.toLowerCase());

  const matchesRisk =
    riskFilter === "All" || node.data.risk === riskFilter;

  return matchesSearch && matchesRisk;
});

const visibleNodeIds = new Set(visibleNodes.map((node) => node.id));

const visibleEdges = edges.filter(
  (edge) =>
    visibleNodeIds.has(edge.source) &&
    visibleNodeIds.has(edge.target)
);


  return (
    <div className="network-graph-container">
        <div className="graph-toolbar">
  <div className="graph-search">
    <Search size={18} />
    <input
      type="text"
      placeholder="Search suppliers, ports, factories..."
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

  <button
    onClick={() => {
      setSearchTerm("");
      setRiskFilter("All");
      setSelectedNode(null);
    }}
  >
    Reset
    setImpactedNodeIds([]);
  </button>
  {selectedNode && (
  <div className="impact-dashboard">
    <div className="impact-dashboard-header">
      <div>
        <h3>Disruption Impact Analysis</h3>
        <p>Downstream analysis for {selectedNode.data.label}</p>
      </div>
      <span>DEMO ANALYSIS</span>
    </div>

    <div className="impact-metrics">
      <div className="impact-metric">
        <strong>{impactedNodes.length}</strong>
        <span>Affected Nodes</span>
      </div>

      <div className="impact-metric">
        <strong>{impactedCountries.length}</strong>
        <span>Countries Affected</span>
      </div>

      <div className="impact-metric high">
        <strong>{highRiskCount}</strong>
        <span>High Risk</span>
      </div>

      <div className="impact-metric medium">
        <strong>{mediumRiskCount}</strong>
        <span>Medium Risk</span>
      </div>
    </div>

    <div className="affected-locations">
      <h4>Affected Locations</h4>

      {impactedCountries.length === 0 ? (
        <p>No downstream impact detected.</p>
      ) : (
        impactedCountries.map((country) => (
          <div className="affected-location" key={country}>
            <span>{country}</span>
            <strong>
              {impactedNodes
                .filter((node) => node.data.country === country)
                .map((node) => node.data.label)
                .join(", ")}
            </strong>
          </div>
        ))
      )}
    </div>
  </div>
)}
</div>
      <div className="graph-canvas">
        <ReactFlow
          nodes={visibleNodes.map((node) => ({
  ...node,
  data: {
    ...node.data,
    isImpacted: impactedNodeIds.includes(node.id),
  },
}))}
          edges={visibleEdges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={(_, node) => {
  setSelectedNode(node);

  const downstream = getDownstreamNodeIds(
    node.id,
    edges
  );

  setImpactedNodeIds(downstream);
}}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.3}
          maxZoom={2}
          proOptions={{ hideAttribution: false }}
        >
          <Background color="#344253" gap={22} size={1} />
          <Controls />

          <MiniMap
            nodeColor={(node) => {
              if (node.data.risk === "High") return "#ef6478";
              if (node.data.risk === "Medium") return "#e9b45c";
              return "#40cedf";
            }}
            maskColor="rgba(11, 14, 20, 0.7)"
          />
        </ReactFlow>
      </div>

      {selectedNode && (
        <div className="selected-node">
          <div>
            <strong>{selectedNode.data.label}</strong>
            <p>
              {selectedNode.data.type} · {selectedNode.data.country}
            </p>
          </div>

          <div className="selected-node-risk">
            <div className="impact-count">
  <span>Downstream affected nodes</span>
  <strong>{impactedNodeIds.length}</strong>
</div>
            <span>Risk score</span>
            <strong>{selectedNode.data.riskScore}/100</strong>
            <span className={`risk-badge ${selectedNode.data.risk.toLowerCase()}`}>
              {selectedNode.data.risk}
            </span>
          </div>

          <button onClick={() => setSelectedNode(null)}>
            Close
          </button>
        </div>
      )}
    </div>
  );
}

export default NetworkGraph;

