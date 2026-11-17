
export const initialNodes = [
  {
    id: "port-1",
    position: { x: 100, y: 150 },
    data: {
      label: "Rotterdam Port",
      type: "Port",
      country: "Netherlands",
      risk: "High",
      riskScore: 92,
    },
    className: "high-risk",
  },
  {
    id: "supplier-1",
    position: { x: 400, y: 70 },
    data: {
      label: "European Supplier",
      type: "Supplier",
      country: "Germany",
      risk: "Medium",
      riskScore: 65,
    },
  },
  {
    id: "factory-1",
    position: { x: 700, y: 150 },
    data: {
      label: "Electronics Factory",
      type: "Manufacturer",
      country: "Germany",
      risk: "High",
      riskScore: 85,
    },
    className: "high-risk",
  },
  {
    id: "supplier-2",
    position: { x: 400, y: 330 },
    data: {
      label: "Component Supplier",
      type: "Supplier",
      country: "China",
      risk: "Low",
      riskScore: 25,
    },
  },
  {
    id: "factory-2",
    position: { x: 1000, y: 150 },
    data: {
      label: "North American Factory",
      type: "Manufacturer",
      country: "USA",
      risk: "Medium",
      riskScore: 58,
    },
  },
];

export const initialEdges = [
  {
    id: "e1",
    source: "port-1",
    target: "supplier-1",
    label: "SHIPS TO",
    animated: true,
  },
  {
    id: "e2",
    source: "supplier-1",
    target: "factory-1",
    label: "SUPPLIES",
    animated: true,
  },
  {
    id: "e3",
    source: "supplier-2",
    target: "factory-1",
    label: "COMPONENTS",
  },
  {
    id: "e4",
    source: "factory-1",
    target: "factory-2",
    label: "DISTRIBUTES TO",
    animated: true,
  },
];
