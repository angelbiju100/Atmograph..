
import { Handle, Position } from "@xyflow/react";
import { Ship, Factory, Boxes } from "lucide-react";

function CustomNode({ data, selected }) {
  const nodeType = data.type?.toLowerCase();

  const Icon =
    nodeType === "port"
      ? Ship
      : nodeType === "manufacturer"
      ? Factory
      : Boxes;

  const risk = data.risk?.toLowerCase() || "low";

  return (
    <div
      className={`custom-node ${nodeType} ${risk} ${
        selected ? "selected" : ""
      } ${data.isImpacted ? "impacted" : ""}`}
    >
      <Handle type="target" position={Position.Left} />

      {data.isImpacted && (
        <span className="impact-label">IMPACTED</span>
      )}

      <div className="custom-node-header">
        <div className="custom-node-icon">
          <Icon size={19} />
        </div>

        <span className={`node-risk ${risk}`}>
          {data.risk} Risk
        </span>
      </div>

      <div className="custom-node-info">
        <strong>{data.label}</strong>
        <span>{data.country}</span>
      </div>

      <div className="custom-node-footer">
        <span>{data.type}</span>
        <strong>{data.riskScore}/100</strong>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default CustomNode;

