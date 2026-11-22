
import { useEffect, useState, useCallback } from "react";

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
  addEdge,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { getNodeNeighbors } from "../services/networkApi";

function NetworkNode({ data }) {
  return (
    <div
      style={{
        background: data.selected ? "#123b35" : "#172033",
        border: `2px solid ${data.selected ? "#10b981" : "#475569"}`,
        borderRadius: "12px",
        padding: "12px 18px",
        minWidth: "130px",
        color: "#ffffff",
        textAlign: "center",
        boxShadow: data.selected
          ? "0 0 18px rgba(16,185,129,0.25)"
          : "none",
      }}
    >
      <Handle type="target" position={Position.Left} />

      <strong>{data.label}</strong>

      <div
        style={{
          fontSize: "11px",
          color: "#94a3b8",
          marginTop: "5px",
        }}
      >
        {data.location || "Unknown location"}
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = {
  networkNode: NetworkNode,
};

function VisualNetworkExplorer() {
  const [selectedNode, setSelectedNode] = useState("n5063");
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [neighborCounts, setNeighborCounts] = useState({
    incoming: 0,
    outgoing: 0,
  });

  const onConnect = useCallback(
    (params) => setEdges((current) => addEdge(params, current)),
    [setEdges]
  );

  const loadNetwork = useCallback(async (nodeId) => {
    try {
      setLoading(true);
      setError("");

      const result = await getNodeNeighbors(nodeId);

      const centerNode = {
        id: nodeId,
        type: "networkNode",
        position: { x: 350, y: 220 },
        data: {
          label: nodeId,
          location: "Selected node",
          selected: true,
        },
      };

      const incomingNodes = result.incoming_neighbors.map(
        (node, index) => ({
          id: node.id,
          type: "networkNode",
          position: {
            x: 30,
            y: 70 + index * 110,
          },
          data: {
            label: node.id,
            location: node.location,
            selected: false,
          },
        })
      );

      const outgoingNodes = result.outgoing_neighbors.map(
        (node, index) => ({
          id: node.id,
          type: "networkNode",
          position: {
            x: 670,
            y: 70 + index * 110,
          },
          data: {
            label: node.id,
            location: node.location,
            selected: false,
          },
        })
      );

      const incomingEdges = result.incoming_neighbors.map(
        (node) => ({
          id: `${node.id}-${nodeId}`,
          source: node.id,
          target: nodeId,
          animated: true,
          style: { stroke: "#3b82f6", strokeWidth: 2 },
        })
      );

      const outgoingEdges = result.outgoing_neighbors.map(
        (node) => ({
          id: `${nodeId}-${node.id}`,
          source: nodeId,
          target: node.id,
          animated: true,
          style: { stroke: "#10b981", strokeWidth: 2 },
        })
      );

      setNodes([
        ...incomingNodes,
        centerNode,
        ...outgoingNodes,
      ]);

      setEdges([
        ...incomingEdges,
        ...outgoingEdges,
      ]);

      setNeighborCounts({
        incoming: result.incoming_count,
        outgoing: result.outgoing_count,
      });
    } catch (err) {
      console.error("Visual network error:", err);
      setError(
        err.response?.data?.detail ||
        "Unable to load network connections."
      );
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    loadNetwork(selectedNode);
  }, [selectedNode, loadNetwork]);

  const handleNodeClick = useCallback((event, node) => {
    if (node.id !== selectedNode) {
      setSelectedNode(node.id);
    }
  }, [selectedNode]);

  return (
    <div className="risk-table-section">
      <div className="risk-table-heading">
        <div>
          <h2>Visual Network Explorer</h2>
          <p>
            Explore direct incoming and outgoing network
            connections using live AnonNet data.
          </p>
        </div>

        <span className="live-tag">INTERACTIVE GRAPH</span>
      </div>

      <div className="risk-table-controls">
        <input
          type="text"
          value={selectedNode}
          onChange={(e) => setSelectedNode(e.target.value.trim())}
          placeholder="Enter a node ID, e.g. n5063"
        />

        <button
          onClick={() => loadNetwork(selectedNode)}
          disabled={loading || !selectedNode}
        >
          {loading ? "Loading..." : "Explore Node"}
        </button>
      </div>

      <div className="risk-overview-grid">
        <div className="risk-overview-card total">
          <span>Incoming Nodes</span>
          <h2>{neighborCounts.incoming}</h2>
        </div>

        <div className="risk-overview-card medium">
          <span>Outgoing Nodes</span>
          <h2>{neighborCounts.outgoing}</h2>
        </div>
      </div>

      {error && <p role="alert">{error}</p>}

      {loading && <p>Loading network connections...</p>}

      <div
        style={{
          width: "100%",
          height: "560px",
          borderRadius: "12px",
          overflow: "hidden",
          border: "1px solid #334155",
          background: "#0f172a",
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
        >
          <Background color="#475569" gap={20} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      <p className="demo-notice">
        Blue edges represent incoming connections.
        Green edges represent outgoing connections.
        Directions follow the original AnonNet edge data.
      </p>
    </div>
  );
}

export default VisualNetworkExplorer;
