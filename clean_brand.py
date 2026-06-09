import json

INPUT_FILE = "brand.json"
OUTPUT_FILE = "brand.json"

def consolidate_brand_data():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Could not find '{INPUT_FILE}'. Please ensure it's in this folder.")
        return


    consolidated = {}

    for entry in raw_data:
        name = entry.get("name")
        domain = entry.get("domain")
        country = entry.get("country")
        branding = entry.get("branding", {})

        if not name:
            continue

        if name not in consolidated:
            
            consolidated[name] = {
                "name": name,
                "domains": [domain] if domain else [],
                "country": country,
                "branding": {
                    "logo": branding.get("logo"),
                    "shield": branding.get("shield"),
                    "wordmark": branding.get("wordmark")
                }
            }
        else:
            
            if domain and domain not in consolidated[name]["domains"]:
                consolidated[name]["domains"].append(domain)
            
          
            current_branding = consolidated[name]["branding"]
            if not current_branding["logo"] and branding.get("logo"):
                current_branding["logo"] = branding.get("logo")
            if not current_branding["shield"] and branding.get("shield"):
                current_branding["shield"] = branding.get("shield")
            if not current_branding["wordmark"] and branding.get("wordmark"):
                current_branding["wordmark"] = branding.get("wordmark")

   
    cleaned_list = list(consolidated.values())

   
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned_list, f, indent=2, ensure_ascii=False)

    print("---  DATA CLEANING METRICS ---")
    print(f" Original entry count: {len(raw_data)}")
    print(f" Consolidated unique entries: {len(cleaned_list)}")
    print(f" Cleaned dataset successfully saved to: '{OUTPUT_FILE}'")

if __name__ == "__main__":
    consolidate_brand_data()