// src/components/RiskSummary.jsx
export default function RiskSummary({ riskData }) {
  if (!riskData) {
    return (
      <div className="card">
        <h2>Risk Summary</h2>
        <p>No risk calculated yet. Enter a regimen and click "Check Risk".</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Risk Summary</h2>
      <p>
        <strong>Risk score:</strong> {riskData.risk_score?.toFixed(2)}
      </p>
      <p>
        <strong>Total pairs:</strong> {riskData.total_pairs}
      </p>
      <p>
        <strong>Severe interactions:</strong> {riskData.severe_pairs}
      </p>
      <p>
        <strong>Moderate interactions:</strong> {riskData.moderate_pairs}
      </p>
      <p>
        <strong>Unknown interactions:</strong> {riskData.unknown_pairs}
      </p>
    </div>
  );
}
