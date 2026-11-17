import { useState } from "react";
import Predictions from "./components/Predictions";
import NetworkGraph from "./components/NetworkGraph";
import {
  Activity,
  Network,
  ShieldAlert,
  TrendingUp,
  Newspaper,
  Settings,
  Search,
  Bell,
  ArrowUpRight,
  AlertTriangle,
  Globe2,
  Clock3,
  Menu,
} from "lucide-react";

import "./App.css";

const navigation = [
  { name: "Dashboard", icon: Activity },
  { name: "Supply Network", icon: Network },
  { name: "Risk Monitoring", icon: ShieldAlert },
  { name: "Predictions", icon: TrendingUp },
  { name: "Disruptions", icon: Newspaper },
];

const stats = [
  {
    title: "Suppliers Monitored",
    value: "2,840",
    change: "+12.8%",
    icon: Globe2,
  },
  {
    title: "Active Disruptions",
    value: "24",
    change: "+4.2%",
    icon: AlertTriangle,
  },
  {
    title: "High Risk Nodes",
    value: "18",
    change: "-2.4%",
    icon: ShieldAlert,
  },
  {
    title: "Predicted Delays",
    value: "156",
    change: "+8.6%",
    icon: Clock3,
  },
];

const alerts = [
  {
    title: "Port congestion detected",
    location: "Rotterdam, Netherlands",
    risk: "High",
    time: "12 min ago",
  },
  {
    title: "Supplier capacity reduced",
    location: "Shanghai, China",
    risk: "Medium",
    time: "38 min ago",
  },
  {
    title: "Weather disruption reported",
    location: "Hamburg, Germany",
    risk: "High",
    time: "1 hr ago",
  },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Network size={24} />
          </div>
          <div>
            <h2>AtmoGraph</h2>
            <span>SUPPLY INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-section">
          <p className="nav-label">WORKSPACE</p>

          {navigation.map((item, index) => {
            const Icon = item.icon;

            return (
              <button
                className={`nav-item ${
  activePage === item.name ? "active" : ""
}`}
key={item.name}
onClick={() => setActivePage(item.name)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </div>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="system-status">
            <span className="status-dot"></span>
            System operational
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <Menu size={20} className="mobile-menu" />
            <span>Workspace</span>
            <span className="breadcrumb-divider">/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <Search size={17} />
              <input placeholder="Search network..." />
              <span>⌘ K</span>
            </div>

            <button className="icon-button">
              <Bell size={19} />
              <span className="notification-dot"></span>
            </button>

            <div className="profile">
              <div className="avatar">AB</div>
              <div className="profile-info">
                <strong>Analyst</strong>
                <span>Administrator</span>
              </div>
            </div>
          </div>
        </header>

        <section className="dashboard">
          {activePage === "Predictions" ? (
  <>
    <div className="page-heading">
      <div>
        <p className="eyebrow">ANALYTICS / FORECASTING</p>
        <h1>Predictions & Forecasts</h1>
        <p className="subtitle">
          Explore projected supply chain disruption risks.
        </p>
      </div>
    </div>

    <Predictions />

    <div className="footer-note">
      <span>ATMOGRAPH INTELLIGENCE PLATFORM</span>
      <span>DEMO DATA · FRONTEND DEVELOPMENT</span>
    </div>
  </>
) : activePage === "Dashboard" ? ( <>
          <div className="page-heading">
            <div>
              <p className="eyebrow">OVERVIEW / 2026</p>
              <h1>Supply Chain Intelligence</h1>
              <p className="subtitle">
                Monitor disruptions. Understand risks. Predict what happens next.
              </p>
            </div>

            <button className="date-button">
              <Clock3 size={16} />
              Last 30 days
            </button>
          </div>

          <div className="stats-grid">
            {stats.map((stat) => {
              const Icon = stat.icon;

              return (
                <div className="stat-card" key={stat.title}>
                  <div className="stat-top">
                    <span>{stat.title}</span>
                    <Icon size={19} />
                  </div>

                  <div className="stat-value">{stat.value}</div>

                  <div className="stat-change">
                    <ArrowUpRight size={15} />
                    {stat.change}
                    <span>vs last month</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="content-grid">
            <section className="panel network-panel">
              <div className="panel-heading">
                <div>
                  <h2>Supply Network Overview</h2>
                  <p>Visualize connections across your global supply chain</p>
                </div>
                <span className="live-tag">
                  <span className="status-dot"></span>
                  LIVE MONITORING
                </span>
              </div>

              <NetworkGraph />

              <div className="graph-footer">
                <span><i className="legend-dot blue"></i> Suppliers</span>
                <span><i className="legend-dot purple"></i> Manufacturers</span>
                <span><i className="legend-dot red"></i> High risk</span>
              </div>
            </section>

            <section className="panel alerts-panel">
              <div className="panel-heading">
                <div>
                  <h2>Risk Alerts</h2>
                  <p>Latest supply chain disruptions</p>
                </div>
                <button className="text-button">View all</button>
              </div>

              <div className="alerts-list">
                {alerts.map((alert) => (
                  <div className="alert-item" key={alert.title}>
                    <div className="alert-icon">
                      <AlertTriangle size={18} />
                    </div>

                    <div className="alert-details">
                      <strong>{alert.title}</strong>
                      <span>{alert.location}</span>
                      <small>{alert.time}</small>
                    </div>

                    <span className={`risk-badge ${alert.risk.toLowerCase()}`}>
                      {alert.risk}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="footer-note">
            <span>ATMOGRAPH INTELLIGENCE PLATFORM</span>
            <span>DEMO DATA · FRONTEND DEVELOPMENT</span>
          </div>
          </>
          ) : (
  <div className="page-heading">
    <div>
      <p className="eyebrow">ATMOGRAPH / WORKSPACE</p>
      <h1>{activePage}</h1>
      <p className="subtitle">
        This section is under development.
      </p>
    </div>
  </div>
)}
        </section>
      </main>
    </div>
  );
}

export default App;
