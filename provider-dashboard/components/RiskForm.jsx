// src/components/RiskForm.jsx
import { useState } from "react";
import { getRiskScore, getRecommendations } from "../api";

export default function RiskForm({ setRiskData, setRecommendations }) {
  const [drugInput, setDrugInput] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("M");
  const [targetDrug, setTargetDrug] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const parseDrugIds = () =>
    drugInput
      .split(/[,\s]+/)
      .map((d) => d.trim())
      .filter(Boolean);

  async function handleRiskCheck(e) {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      const ids = parseDrugIds();
      if (!ids.length) {
        setErrorMsg("Please enter at least one drug ID.");
        setLoading(false);
        return;
      }
      const risk = await getRiskScore(ids, age, sex);
      setRiskData(risk);
    } catch (err) {
      console.error(err);
      setErrorMsg("Error fetching risk. Check backend and IDs.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRecommend(e) {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      const ids = parseDrugIds();
      if (!ids.length) {
        setErrorMsg("Please enter at least one drug ID.");
        setLoading(false);
        return;
      }
      if (!targetDrug) {
        setErrorMsg("Please enter target drug ID to replace.");
        setLoading(false);
        return;
      }
      const recs = await getRecommendations(ids, targetDrug.trim());
      setRecommendations(recs);
    } catch (err) {
      console.error(err);
      setErrorMsg("Error fetching recommendations.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Drug Regimen Risk Check</h2>
      <form className="form" onSubmit={handleRiskCheck}>
        <label>
          Drug IDs (comma or space separated):
          <input
            type="text"
            value={drugInput}
            onChange={(e) => setDrugInput(e.target.value)}
            placeholder="e.g. DB00001 DB00316 DB00133"
          />
        </label>

        <div className="inline-fields">
          <label>
            Age:
            <input
              type="number"
              min="0"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="optional"
            />
          </label>
          <label>
            Sex:
            <select value={sex} onChange={(e) => setSex(e.target.value)}>
              <option value="M">M</option>
              <option value="F">F</option>
            </select>
          </label>
        </div>

        <div className="buttons-row">
          <button type="submit" disabled={loading}>
            {loading ? "Checking..." : "Check Risk"}
          </button>
        </div>

        <hr />

        <label>
          Target drug to replace (ID):
          <input
            type="text"
            value={targetDrug}
            onChange={(e) => setTargetDrug(e.target.value)}
            placeholder="must be one of the above IDs"
          />
        </label>

        <div className="buttons-row">
          <button onClick={handleRecommend} disabled={loading}>
            {loading ? "Recommending..." : "Get Alternatives"}
          </button>
        </div>

        {errorMsg && <p className="error">{errorMsg}</p>}
      </form>
    </div>
  );
}
