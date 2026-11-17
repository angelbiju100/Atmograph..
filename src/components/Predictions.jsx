
import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const forecastData = {
  30: [
    { day: "Day 1", risk: 35 },
    { day: "Day 10", risk: 45 },
    { day: "Day 20", risk: 61 },
    { day: "Day 30", risk: 72 },
  ],
  60: [
    { day: "Day 1", risk: 35 },
    { day: "Day 20", risk: 52 },
    { day: "Day 40", risk: 68 },
    { day: "Day 60", risk: 81 },
  ],
  90: [
    { day: "Day 1", risk: 35 },
    { day: "Day 30", risk: 58 },
    { day: "Day 60", risk: 74 },
    { day: "Day 90", risk: 89 },
  ],
};

const metrics = {
  30: { risk: "72%", delays: "156", suppliers: "18" },
  60: { risk: "81%", delays: "214", suppliers: "26" },
  90: { risk: "89%", delays: "302", suppliers: "34" },
};

const vulnerableSuppliers = [
  { name: "European Supplier", location: "Germany", risk: 92 },
  { name: "Shanghai Components", location: "China", risk: 85 },
  { name: "Rotterdam Logistics", location: "Netherlands", risk: 78 },
  { name: "North American Parts", location: "USA", risk: 68 },
];

function Predictions() {
  const [period, setPeriod] = useState(30);

  return (
    <div className="predictions-page">
      <div className="forecast-header">
        <div>
          <h2>Supply Chain Risk Forecast</h2>
          <p>Projected disruption risk across your supply network.</p>
        </div>

        <div className="forecast-controls">
          {[30, 60, 90].map((days) => (
            <button
              key={days}
              className={period === days ? "active" : ""}
              onClick={() => setPeriod(days)}
            >
              {days} Days
            </button>
          ))}
        </div>
      </div>

      <div className="prediction-metrics">
        <div className="prediction-card">
          <span>Risk Index</span>
          <strong>{metrics[period].risk}</strong>
          <small>Projected risk level</small>
        </div>

        <div className="prediction-card">
          <span>Predicted Delays</span>
          <strong>{metrics[period].delays}</strong>
          <small>Estimated delayed shipments</small>
        </div>

        <div className="prediction-card">
          <span>At-Risk Suppliers</span>
          <strong>{metrics[period].suppliers}</strong>
          <small>Suppliers requiring attention</small>
        </div>
      </div>

      <div className="forecast-chart">
        <h3>Risk Trend — Next {period} Days</h3>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecastData[period]}>
            <CartesianGrid strokeDasharray="3 3" stroke="#293446" />
            <XAxis dataKey="day" stroke="#8996a8" />
            <YAxis domain={[0, 100]} stroke="#8996a8" />
            <Tooltip
              contentStyle={{
                background: "#151c27",
                border: "1px solid #293446",
                borderRadius: "8px",
              }}
            />
            <Line
              type="monotone"
              dataKey="risk"
              name="Risk Index"
              stroke="#40cedf"
              strokeWidth={3}
              dot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="vulnerable-panel">
        <h3>Most Vulnerable Suppliers</h3>
        <p>Ranked by illustrative risk score.</p>

        {vulnerableSuppliers.map((supplier) => (
          <div className="supplier-risk-row" key={supplier.name}>
            <div className="supplier-details">
              <strong>{supplier.name}</strong>
              <span>{supplier.location}</span>
            </div>

            <div className="supplier-risk-score">
              <div className="risk-progress">
                <div
                  style={{ width: `${supplier.risk}%` }}
                />
              </div>
              <strong>{supplier.risk}/100</strong>
            </div>
          </div>
        ))}
      </div>

      <p className="demo-notice">
        DEMO DATA — Illustrative forecast values, not actual model predictions.
      </p>
    </div>
  );
}

export default Predictions;

