import xml.etree.ElementTree as ET
import pandas as pd

DRUGBANK_FILE = "../data_raw/drugbank/drugbank.xml"

def strip_tag(tag):
    """Remove XML namespace, e.g. '{http://www.drugbank.ca}drug' -> 'drug'."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def guess_severity(description: str) -> str:
    """Very rough heuristic based on text."""
    if not description:
        return ""
    desc_low = description.lower()
    if "life-threatening" in desc_low or "contraindicated" in desc_low or "severe" in desc_low:
        return "severe"
    if "monitor" in desc_low or "increase" in desc_low or "decrease" in desc_low or "adjust" in desc_low:
        return "moderate"
    return "unknown"

def parse_interactions(limit_drugs=None):
    print(f"Loading XML from: {DRUGBANK_FILE}")
    tree = ET.parse(DRUGBANK_FILE)
    root = tree.getroot()

    interactions = []
    drug_count = 0

    for drug in root:
        if strip_tag(drug.tag) != "drug":
            continue

        # Get main drug ID (primary)
        main_id = None
        for child in drug:
            tag = strip_tag(child.tag)
            if tag == "drugbank-id" and child.attrib.get("primary") == "true":
                main_id = (child.text or "").strip()
                break

        if not main_id:
            continue

        # Find <drug-interactions>
        for child in drug:
            if strip_tag(child.tag) == "drug-interactions":
                for di in child:
                    if strip_tag(di.tag) != "drug-interaction":
                        continue

                    other_id = ""
                    description = ""
                    for di_child in di:
                        di_tag = strip_tag(di_child.tag)
                        if di_tag == "drugbank-id":
                            other_id = (di_child.text or "").strip()
                        elif di_tag == "description":
                            description = (di_child.text or "").strip()

                    if main_id and other_id:
                        severity = guess_severity(description)
                        # normalize pair order (so (A,B) and (B,A) count once)
                        a, b = sorted([main_id, other_id])
                        interactions.append({
                            "drug1_id": a,
                            "drug2_id": b,
                            "severity": severity,
                            "description": description,
                            "source": "DrugBank"
                        })

        drug_count += 1
        if limit_drugs is not None and drug_count >= limit_drugs:
            break

    print(f"Collected {len(interactions)} raw interaction rows")
    df = pd.DataFrame(interactions)

    if not df.empty:
        # Drop duplicates of same pair
        df = df.drop_duplicates(subset=["drug1_id", "drug2_id", "description"])
    print(f"After deduplication: {len(df)} interactions")
    return df

def main():
    # First run with a limit just to test quickly
    df = parse_interactions(limit_drugs=300)  # change to None later for full run

    print("Sample interactions:")
    print(df.head())

    df.to_csv("../data_processed/known_interactions.csv", index=False)
    print("Saved to ../data_processed/known_interactions.csv")

if __name__ == "__main__":
    main()
