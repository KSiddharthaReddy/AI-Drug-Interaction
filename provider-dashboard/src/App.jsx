// src/App.jsx
import { useState } from "react";
import RiskForm from "/components/RiskForm.jsx";
import RiskSummary from "/components/RiskSummary.jsx";
import RecommendationList from "/components/RecommendationList.jsx";
import GraphView from "/components/GraphView.jsx";
import "./styles.css";

export default function App() {
  const [riskData, setRiskData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Drug Interaction Clinical Dashboard</h1>
        <p>Check regimen risk, visualize interactions, and explore safer alternatives.</p>
      </header>

      <main className="layout">
        <section className="left-column">
          <RiskForm
            setRiskData={setRiskData}
            setRecommendations={setRecommendations}
          />
          <RiskSummary riskData={riskData} />
          <RecommendationList recommendations={recommendations} />
        </section>
        <section className="right-column">
          <GraphView />
        </section>
      </main>
    </div>
  );
}
