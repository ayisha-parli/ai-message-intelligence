import os
import json
import pandas as pd
from app import classify_message, extract_task_or_event, mask_text

# Create 'output' directory if it doesn't exist
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Load the dataset
csv_path = "messages.csv"

if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found in the current directory.")
else:
    df = pd.read_csv(csv_path)

    classifications = []
    extracted_tasks = []
    sensitive_detected = []

    for _, row in df.iterrows():
        msg_id = str(row.get("Message ID", row.get("message_id", "")))
        text = str(row.get("Message", row.get("message", "")))

        # Part 3: Sensitive Info Check & Masking
        masked_text, sens_findings = mask_text(text)

        # Part 1: Classification
        cls_res = classify_message(masked_text)
        cls_res["message_id"] = msg_id
        classifications.append(cls_res)

        # Part 2: Task / Event Extraction
        task_res = extract_task_or_event(msg_id, masked_text)
        if task_res:
            extracted_tasks.append(task_res)

        # Append Sensitive Info results
        if sens_findings:
            for f in sens_findings:
                f["message_id"] = msg_id
                sensitive_detected.append(f)

    # Save output/classifications.json
    with open(os.path.join(output_dir, "classifications.json"), "w") as f:
        json.dump(classifications, f, indent=2)

    # Save output/extracted_tasks.json
    with open(os.path.join(output_dir, "extracted_tasks.json"), "w") as f:
        json.dump(extracted_tasks, f, indent=2)

    # Save output/sensitive_detected.json
    with open(os.path.join(output_dir, "sensitive_detected.json"), "w") as f:
        json.dump(sensitive_detected, f, indent=2)

    print("Success! Generated 3 output JSON files in the 'output/' folder.")