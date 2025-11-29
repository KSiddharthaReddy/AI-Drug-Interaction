// src/api.js
export const API_BASE = "http://127.0.0.1:8000"; 
// change to your machine IP if using from mobile or another device

export async function getRiskScore(drugIds, age, sex) {
  const payload = { drug_ids: drugIds };

  if (age !== undefined && age !== null && age !== "") {
    payload.age = Number(age);
  }
  if (sex) {
    payload.sex = sex;
  }

  const res = await fetch(`${API_BASE}/risk_score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Risk API error: ${res.status}`);
  }

  const data = await res.json();
  return data.risk;
}

export async function getRecommendations(drugIds, targetDrug) {
  const payload = {
    drug_ids: drugIds,
    target_drug: targetDrug,
  };

  const res = await fetch(`${API_BASE}/recommend_drug`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Recommend API error: ${res.status}`);
  }

  const data = await res.json();
  return data.recommendations || [];
}

export async function getInteractionGraph() {
  const res = await fetch(`${API_BASE}/interaction_graph`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error(`Graph API error: ${res.status}`);
  }

  return res.json();
}
