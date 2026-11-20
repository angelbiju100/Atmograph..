
import { useState } from "react";
import { initialNodes, initialEdges } from "../data/mockGraph";
import { getDownstreamNodeIds } from "../components/NetworkGraph";
import {
  AlertTriangle,
  MapPin,
  CalendarDays,
  Search,
  Activity,
} from "lucide-react";

function Disruptions() {
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [sortOrder, setSortOrder] = useState("newest");
  const [typeFilter, setTypeFilter] = useState("All");

  const disruptionEvents = [
    {
      id: 1,
      title: "Port Congestion",
      location: "Rotterdam, Netherlands",
      type: "Logistics",
      sourceNodeId: "port-1",
      severity: "Critical",
      status: "Active",
      date: "20 Nov 2026",
      affected: 3,
      description:
        "Severe congestion at Rotterdam Port is causing potential shipping delays across connected suppliers.",
    },
    {
      id: 2,
      title: "Extreme Weather Conditions",
      location: "Hamburg, Germany",
      type: "Weather",
      sourceNodeId: null,
      severity: "High",
      status: "Active",
      date: "19 Nov 2026",
      affected: 2,
      description:
        "Adverse weather conditions may affect port operations and transportation routes.",
    },
    {
      id: 3,
      title: "Component Supply Shortage",
      location: "Shenzhen, China",
      type: "Supply",
      sourceNodeId: "supplier-2",
      severity: "Medium",
      status: "Monitoring",
      date: "18 Nov 2026",
      affected: 2,
      description:
        "A shortage of electronic components may affect manufacturing schedules.",
    },
    {
      id: 4,
      title: "Transportation Delays",
      location: "Berlin, Germany",
      type: "Transport",
      sourceNodeId: null,
      severity: "Low",
      status: "Resolved",
      date: "16 Nov 2026",
      affected: 1,
      description:
        "A temporary transportation delay has been resolved.",
    },
  ];

  const filteredEvents = disruptionEvents.filter((event) => {
    const search = searchTerm.toLowerCase().trim();

    const matchesSearch =
      event.title.toLowerCase().includes(search) ||
      event.location.toLowerCase().includes(search) ||
      event.type.toLowerCase().includes(search);

    const matchesSeverity =
    severityFilter === "All" ||
    event.severity === severityFilter;

    const matchesType =
    typeFilter === "All" ||
    event.type === typeFilter;

return matchesSearch && matchesSeverity && matchesType;
  });
  const sortedEvents = [...filteredEvents].sort((a, b) => {
  const severityOrder = {
    Critical: 4,
    High: 3,
    Medium: 2,
    Low: 1,
  };

  if (sortOrder === "newest") {
    return a.id - b.id;
  }

  if (sortOrder === "oldest") {
    return b.id - a.id;
  }

  if (sortOrder === "highest") {
    return severityOrder[b.severity] - severityOrder[a.severity];
  }

  if (sortOrder === "lowest") {
    return severityOrder[a.severity] - severityOrder[b.severity];
  }

  return 0;
});
  const impactedNodeIds = selectedEvent?.sourceNodeId
  ? getDownstreamNodeIds(selectedEvent.sourceNodeId, initialEdges)
  : [];

const impactedNodes = initialNodes.filter((node) =>
  impactedNodeIds.includes(node.id)
);  
  const resolvedCount = filteredEvents.filter(
  (event) => event.status === "Resolved"
).length;

const highSeverityCount = filteredEvents.filter(
  (event) =>
    event.severity === "Critical" ||
    event.severity === "High"
).length;

  return (
    <div className="disruptions-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">INTELLIGENCE / DISRUPTIONS</p>
          <h1>Disruptions</h1>
          <p className="subtitle">
            Monitor supply-chain disruption events and
            investigate potential network-wide impacts.
          </p>
        </div>
      </div>

      <div className="disruption-overview">
        <div className="disruption-stat">
          <AlertTriangle size={20} />
          <span>Total Events</span>
          <h2>{filteredEvents.length}</h2>
        </div>

        <div className="disruption-stat">
          <Activity size={20} />
          <span>Active Events</span>
          <h2>
            {filteredEvents.filter(
              (event) => event.status === "Active"
            ).length}
          </h2>
        </div>

        <div className="disruption-stat">
          <AlertTriangle size={20} />
          <span>Critical Events</span>
          <h2>
            {filteredEvents.filter(
              (event) => event.severity === "Critical"
            ).length}
          </h2>
        </div>

       <div className="disruption-stat">
        <Activity size={20} />
        <span>Resolved Events</span>
        <h2>{resolvedCount}</h2>
        </div>

        <div className="disruption-stat">
        <AlertTriangle size={20} />
        <span>High-Severity Events</span>
        <h2>{highSeverityCount}</h2>
        </div>
      </div>

      <div className="disruption-section">
        <div className="disruption-heading">
          <div>
            <h2>Disruption Event Register</h2>
            <p>Track and investigate reported events.</p>
          </div>
        </div>

        <div className="disruption-controls">
          <div className="disruption-search">
            <Search size={18} />
            <input
              placeholder="Search events or locations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="All">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <select
  value={typeFilter}
  onChange={(e) => setTypeFilter(e.target.value)}
>
  <option value="All">All Event Types</option>
  <option value="Logistics">Logistics</option>
  <option value="Weather">Weather</option>
  <option value="Supply">Supply</option>
  <option value="Transport">Transport</option>
</select>
         <select
  value={sortOrder}
  onChange={(e) => setSortOrder(e.target.value)}
>
  <option value="newest">Newest First</option>
  <option value="oldest">Oldest First</option>
  <option value="highest">Highest Severity</option>
  <option value="lowest">Lowest Severity</option>
</select> 
            <button
  className="reset-filters-btn"
  onClick={() => {
    setSearchTerm("");
    setSeverityFilter("All");
    setTypeFilter("All");
    setSortOrder("newest");
  }}
>
  Reset Filters
    </button>
        </div>

        <div className="disruption-list">
          {filteredEvents.length > 0 ? (
            sortedEvents.map((event) => (
              <div
                className="disruption-card"
                 key={event.id}
                 onClick={() => setSelectedEvent(event)}
                >
                <div className="disruption-card-main">
                  <div className="disruption-icon">
                    <AlertTriangle size={20} />
                  </div>

                  <div className="disruption-info">
                    <h3>{event.title}</h3>

                    <div className="disruption-meta">
                      <span>
                        <MapPin size={13} />
                        {event.location}
                      </span>

                      <span>
                        <CalendarDays size={13} />
                        {event.date}
                      </span>
                    </div>

                    <p>{event.description}</p>
                  </div>
                </div>

                <div className="disruption-card-footer">
                  <span className={`severity-badge ${event.severity.toLowerCase()}`}>
                    {event.severity}
                  </span>

                  <span className="disruption-status">
                    {event.status}
                  </span>

                  <span className="affected-count">
                    {event.affected} affected
                  </span>
                </div>
              </div>
            ))
          ) : (
            <p className="empty-disruptions">
              No matching disruption events found.
            </p>
          )}
        </div>

        {/* DISRUPTION DETAILS PANEL */}
        {selectedEvent && (
          <div className="disruption-details-panel">
            <div className="disruption-details-header">
              <div>
                <p className="eyebrow">EVENT INVESTIGATION</p>
                <h2>{selectedEvent.title}</h2>
                <p>{selectedEvent.location}</p>
              </div>

              <button
                className="close-risk-details"
                onClick={() => setSelectedEvent(null)}
              >
                ✕
              </button>
            </div>

            <div className="disruption-details-grid">
              <div>
                <span>Severity</span>
                <strong>{selectedEvent.severity}</strong>
              </div>

              <div>
                <span>Status</span>
                <strong>{selectedEvent.status}</strong>
              </div>

              <div>
                <span>Affected Entities</span>
                <strong>{selectedEvent.affected}</strong>
              </div>
            </div>

            <div className="disruption-description">
              <h3>Disruption Description</h3>
              <p>{selectedEvent.description}</p>
            </div>

            <div className="disruption-description">
              <h3>Recommended Mitigation</h3>
              <p>
                {selectedEvent.severity === "Critical"
                  ? "Activate alternative routes and suppliers. Escalate the incident for immediate investigation."
                  : selectedEvent.severity === "High"
                  ? "Review alternative transportation routes and closely monitor affected suppliers."
                  : selectedEvent.severity === "Medium"
                  ? "Monitor supplier performance and prepare contingency plans."
                  : "Continue routine monitoring and track the event until fully resolved."}
              </p>
            </div>

<div className="disruption-description impact-analysis">
  <h3>Supply Chain Impact Analysis</h3>
  {selectedEvent.sourceNodeId && (
  <div className="impact-propagation">
    <h4>Disruption Propagation Path</h4>

    <div className="propagation-path">
      <div className="propagation-node source-node">
        <strong>
          {initialNodes.find(
            (node) => node.id === selectedEvent.sourceNodeId
          )?.data.label}
        </strong>
        <span>Disruption Source</span>
      </div>

      {impactedNodes.map((node) => (
        <div className="propagation-step" key={node.id}>
          <span className="propagation-arrow">↓</span>

          <div className="propagation-node">
            <strong>{node.data.label}</strong>
            <span>{node.data.country}</span>
          </div>
        </div>
      ))}
    </div>
  </div>
)}

  {selectedEvent.sourceNodeId ? (
    impactedNodes.length > 0 ? (
      <div className="impacted-entities-list">
        {impactedNodes.map((node) => (
          <div className="impacted-entity" key={node.id}>
            <div>
              <strong>{node.data.label}</strong>
              <span>{node.data.country}</span>
            </div>

            <span className="impact-risk">
              {node.data.risk} Risk
            </span>
          </div>
        ))}
      </div>
    ) : (
      <p>No downstream entities found in the current network.</p>
    )
  ) : (
    <p>
      This event is not yet connected to a supply-chain node.
      Network impact analysis is unavailable.
    </p>
  )}

  {selectedEvent.sourceNodeId && (
    <p className="impact-note">
      Potential downstream impact based on the current network graph.
      These are simulated relationships, not confirmed real-world impacts.
    </p>
  )}
</div>

          </div>
        )}
      </div>
    </div>
  );
}

export default Disruptions;

