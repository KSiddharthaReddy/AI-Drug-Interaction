// src/components/RecommendationList.jsx
export default function RecommendationList({ recommendations }) {
  return (
    <div className="card">
      <h2>Alternative Drug Recommendations</h2>
      {!recommendations || recommendations.length === 0 ? (
        <p>No recommendations yet. Choose a target drug and click "Get Alternatives".</p>
      ) : (
        <ul className="recommendations-list">
          {recommendations.map((rec, idx) => (
            <li key={idx} className="recommendation-item">
              <p>
                <strong>Alternative Drug ID:</strong> {rec.alternative_drug_id}
              </p>
              <p>
                <strong>Risk score:</strong> {rec.risk_score.toFixed(2)}
              </p>
              <p>
                <strong>Severe pairs:</strong> {rec.severe_pairs} |{" "}
                <strong>Moderate:</strong> {rec.moderate_pairs} |{" "}
                <strong>Unknown:</strong> {rec.unknown_pairs}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
