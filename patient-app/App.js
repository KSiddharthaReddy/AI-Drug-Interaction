// App.js
import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  Button,
  ScrollView,
  StyleSheet,
} from "react-native";

const API_BASE = "http://192.168.0.106:8000"; 
// e.g. "http://192.168.0.1:8000"

export default function App() {
  const [drugInput, setDrugInput] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("M");
  const [risk, setRisk] = useState(null);
  const [recs, setRecs] = useState([]);
  const [message, setMessage] = useState("");

  const parseDrugIds = () =>
    drugInput
      .split(/[,\s]+/)
      .map((d) => d.trim())
      .filter(Boolean);

  async function handleRiskCheck() {
    setMessage("");
    setRisk(null);

    const ids = parseDrugIds();
    if (!ids.length) {
      setMessage("Please enter at least one drug ID.");
      return;
    }

    try {
      const payload = { drug_ids: ids };
      if (age) payload.age = Number(age);
      if (sex) payload.sex = sex;

      const res = await fetch(`${API_BASE}/risk_score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("API error");
      }

      const data = await res.json();
      setRisk(data.risk);
    } catch (err) {
      console.error(err);
      setMessage("Error checking risk. Make sure backend is running.");
    }
  }

  async function handleRecommend() {
    setMessage("");
    setRecs([]);

    const ids = parseDrugIds();
    if (!ids.length) {
      setMessage("Please enter at least one drug ID.");
      return;
    }

    // For simplicity, replace the first drug in the list
    const targetDrug = ids[0];

    try {
      const payload = { drug_ids: ids, target_drug: targetDrug };
      const res = await fetch(`${API_BASE}/recommend_drug`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("API error");
      }

      const data = await res.json();
      setRecs(data.recommendations || []);
    } catch (err) {
      console.error(err);
      setMessage("Error fetching recommendations.");
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>Patient Medication Safety Checker</Text>
        <Text style={styles.subtitle}>
          Enter your medications (DrugBank IDs) to estimate interaction risk.
        </Text>

        <View style={styles.card}>
          <Text style={styles.label}>Drug IDs (comma or space separated):</Text>
          <TextInput
            style={styles.input}
            value={drugInput}
            onChangeText={setDrugInput}
            placeholder="DB00001 DB00316 DB00133"
          />

          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>Age:</Text>
              <TextInput
                style={styles.input}
                value={age}
                onChangeText={setAge}
                placeholder="optional"
                keyboardType="numeric"
              />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>Sex (M/F):</Text>
              <TextInput
                style={styles.input}
                value={sex}
                onChangeText={setSex}
                maxLength={1}
              />
            </View>
          </View>

          <View style={styles.buttonRow}>
            <Button title="Check Risk Score" onPress={handleRiskCheck} />
          </View>

          <View style={styles.buttonRow}>
            <Button title="Show Safer Alternatives" onPress={handleRecommend} />
          </View>

          {message ? <Text style={styles.error}>{message}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Risk Summary</Text>
          {!risk ? (
            <Text>No risk calculated yet.</Text>
          ) : (
            <>
              <Text>Risk score: {risk.risk_score?.toFixed(2)}</Text>
              <Text>Total pairs: {risk.total_pairs}</Text>
              <Text>Severe interactions: {risk.severe_pairs}</Text>
              <Text>Moderate interactions: {risk.moderate_pairs}</Text>
              <Text>Unknown interactions: {risk.unknown_pairs}</Text>
            </>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Alternative Recommendations</Text>
          {!recs.length ? (
            <Text>No recommendations yet.</Text>
          ) : (
            recs.map((r, idx) => (
              <View key={idx} style={styles.recItem}>
                <Text>Alternative Drug ID: {r.alternative_drug_id}</Text>
                <Text>Risk score: {r.risk_score.toFixed(2)}</Text>
                <Text>
                  Severe: {r.severe_pairs} | Moderate: {r.moderate_pairs} | Unknown:{" "}
                  {r.unknown_pairs}
                </Text>
              </View>
            ))
          )}
        </View>

        <Text style={styles.disclaimer}>
          Disclaimer: This app is for educational purposes only and does not replace
          professional medical advice.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fb" },
  scroll: { padding: 16 },
  title: { fontSize: 22, fontWeight: "600", textAlign: "center", marginBottom: 8 },
  subtitle: { fontSize: 14, textAlign: "center", color: "#555", marginBottom: 16 },
  card: {
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
  },
  label: { fontSize: 14, marginBottom: 4 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 6,
    marginBottom: 8,
    backgroundColor: "#fff",
  },
  row: { flexDirection: "row", gap: 8 },
  col: { flex: 1 },
  buttonRow: { marginTop: 8 },
  cardTitle: { fontSize: 16, fontWeight: "600", marginBottom: 6 },
  recItem: {
    borderTopWidth: 1,
    borderTopColor: "#eee",
    paddingTop: 6,
    marginTop: 6,
  },
  disclaimer: {
    fontSize: 12,
    color: "#666",
    textAlign: "center",
    marginTop: 12,
    marginBottom: 20,
  },
  error: { color: "#b91c1c", marginTop: 6 },
});
