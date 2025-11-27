import xml.etree.ElementTree as ET
import pandas as pd

# Path to your DrugBank XML file (relative to this script in kg/)
DRUGBANK_FILE = "../data_raw/drugbank/drugbank.xml"

def strip_tag(tag):
    """Remove XML namespace, e.g. '{http://www.drugbank.ca}drug' -> 'drug'."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def parse_drugbank_xml(limit=None):
    print(f"Loading XML from: {DRUGBANK_FILE}")
    tree = ET.parse(DRUGBANK_FILE)
    root = tree.getroot()

    drugs_data = []
    count = 0

    for drug in root:
        if strip_tag(drug.tag) != "drug":
            continue

        drug_type = drug.attrib.get("type", "")

        drug_id = None
        name = ""
        groups = []
        categories = []
        indication = ""

        for child in drug:
            tag = strip_tag(child.tag)

            if tag == "drugbank-id":
                # pick primary ID
                if child.attrib.get("primary") == "true":
                    drug_id = (child.text or "").strip()

            elif tag == "name":
                name = (child.text or "").strip()

            elif tag == "groups":
                for g in child:
                    if strip_tag(g.tag) == "group" and g.text:
                        groups.append(g.text.strip())

            elif tag == "categories":
                # nested categories/category/category
                for cat in child:
                    if strip_tag(cat.tag) == "category":
                        for c2 in cat:
                            if strip_tag(c2.tag) == "category" and c2.text:
                                categories.append(c2.text.strip())

            elif tag == "indication":
                indication = (child.text or "").strip()

        # Only save if we have at least an ID and name
        if drug_id and name:
            drugs_data.append({
                "drug_id": drug_id,
                "name": name,
                "type": drug_type,
                "drug_class": "; ".join(categories) if categories else "; ".join(groups),
                "indication": indication
            })

        count += 1
        if limit is not None and count >= limit:
            break

    print(f"Parsed {len(drugs_data)} drugs from XML")
    return pd.DataFrame(drugs_data)

def main():
    # For first run, parse only first N drugs to test (faster)
    # Change limit=None later to parse all
    df = parse_drugbank_xml(limit=500)   # try 500 first so it’s quick
    print("Sample rows:")
    print(df.head())

    df.to_csv("../data_processed/drugs.csv", index=False)
    print("Saved cleaned file to ../data_processed/drugs.csv")

if __name__ == "__main__":
    main()
