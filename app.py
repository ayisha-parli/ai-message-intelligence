import os
import re
import json
import pandas as pd
import streamlit as st

# Integrated Regex Patterns for Sensitive Data Detection
SENSITIVE_PATTERNS = {
    "one_time_password": (r"\b(?i:otp|code|pin|verification code)[\s:-]*\b(\d{4,8})\b", "high", "do_not_store"),
    "password": (r"\b(?i:password|passcode|pwd)[\s:-]*(\S+)", "critical", "do_not_store"),
    "bank_details": (r"\b(?:\d[ -]*?){13,16}\b", "critical", "do_not_send_external"),
    "auth_token": (
        r"\b(bearer\s+[A-Za-z0-9\-_\.=]+|ghp_[A-Za-z0-9]{36}|eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*)\b",
        "critical", "do_not_store"),
    "personal_identification": (r"\b\d{3}-\d{2}-\d{4}\b", "high", "ask_for_confirmation")
}


def mask_text(text: str) -> tuple[str, list]:
    """Detects sensitive information, masks values, and returns risk & recommendations."""
    findings = []
    masked_text = text

    for s_type, (pattern, risk, rec_action) in SENSITIVE_PATTERNS.items():
        matches = list(re.finditer(pattern, masked_text, flags=re.IGNORECASE))
        if matches:
            for m in matches:
                matched_str = m.group(0)
                # Mask sensitive portion
                masked_val = re.sub(r"[A-Za-z0-9]", "*", matched_str)
                masked_text = masked_text.replace(matched_str, masked_val)
                findings.append({
                    "sensitivity_type": s_type,
                    "risk": risk,
                    "recommended_action": rec_action,
                    "masked_text": masked_text
                })

    return masked_text, findings


def classify_message(text: str) -> dict:
    """Rule-assisted lightweight classifier for deterministic results."""
    text_lower = text.lower()

    # Check sensitive keywords first
    if any(k in text_lower for k in ["otp", "password", "pin", "cvv", "bearer"]):
        return {
            "category": "sensitive_information",
            "confidence": 0.95,
            "reason": "Contains authentication credential keywords or secret values."
        }
    elif any(k in text_lower for k in ["meeting", "zoom", "call", "google meet", "schedule", "calendar"]):
        return {
            "category": "meeting_or_event",
            "confidence": 0.92,
            "reason": "Contains event scheduling or meeting invitation keywords."
        }
    elif any(k in text_lower for k in ["please", "submit", "deadline", "todo", "action required", "urgently"]):
        return {
            "category": "action_required",
            "confidence": 0.88,
            "reason": "Contains explicit action requests or deadlines."
        }
    elif any(k in text_lower for k in ["sale", "discount", "offer", "% off", "subscribe", "buy"]):
        return {
            "category": "promotional",
            "confidence": 0.90,
            "reason": "Contains marketing, discount, or promotional triggers."
        }
    elif any(k in text_lower for k in ["my address", "my phone", "i live", "personal"]):
        return {
            "category": "personal_information",
            "confidence": 0.85,
            "reason": "Refers to personal contact or user details."
        }
    else:
        return {
            "category": "general_information",
            "confidence": 0.80,
            "reason": "Informational content with no explicit action triggers."
        }


def extract_task_or_event(msg_id: str, text: str) -> dict | None:
    """Extracts task/event details using simple regex patterns without inventing data."""
    text_lower = text.lower()

    # Check if message contains a task or event
    is_event = any(k in text_lower for k in ["meeting", "sync", "call", "webinar", "conference"])
    is_task = any(k in text_lower for k in ["submit", "complete", "deadline", "send", "review"])

    if not (is_event or is_task):
        return None

    # Date extraction (YYYY-MM-DD or standard patterns)
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b", text)
    extracted_date = date_match.group(0) if date_match else None

    # Time extraction
    time_match = re.search(r"\b\d{1,2}(:\d{2})?\s*(?:am|pm|AM|PM)\b", text)
    extracted_time = time_match.group(0) if time_match else None

    # Priority assessment
    priority = "high" if any(k in text_lower for k in ["urgent", "asap", "priority"]) else "medium"

    return {
        "item_id": f"ITEM_{msg_id}",
        "type": "event" if is_event else "task",
        "title": text[:40] + ("..." if len(text) > 40 else ""),
        "deadline": extracted_date,
        "time": extracted_time,
        "person": None,  # Strictly null if not explicitly detected
        "priority": priority,
        "source_message_id": msg_id
    }


# ---------------- Streamlit Web Application Interface ----------------

st.set_page_config(page_title="AI Message Intelligence System", layout="wide")
st.title("🛡️ Privacy-Preserving AI Message Intelligence System")

uploaded_file = st.sidebar.file_uploader("Upload Message CSV Dataset", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success(f"Loaded {len(df)} messages successfully!")

    # Tab views for submission Requirements
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Message Classification",
        "📅 Tasks & Events",
        "🔒 Sensitive Data Detection",
        "🔍 Mandatory Demo IDs Filter"
    ])

    processed_records = []
    task_records = []
    sensitive_records = []

    for _, row in df.iterrows():
        msg_id = str(row.get("Message ID", row.get("message_id", "")))
        text = str(row.get("Message", row.get("message", "")))

        # Part 3: Masking check first
        masked_text, sens_findings = mask_text(text)

        # Part 1: Classification
        cls_res = classify_message(masked_text)
        cls_res["message_id"] = msg_id
        processed_records.append(cls_res)

        # Part 2: Task Extraction
        task_res = extract_task_or_event(msg_id, masked_text)
        if task_res:
            task_records.append(task_res)

        if sens_findings:
            for f in sens_findings:
                f["message_id"] = msg_id
                sensitive_records.append(f)

    with tab1:
        st.subheader("Part 1: Message Classification Results")
        st.dataframe(pd.DataFrame(processed_records))

    with tab2:
        st.subheader("Part 2: Extracted Tasks & Events")
        st.dataframe(pd.DataFrame(task_records))

    with tab3:
        st.subheader("Part 3: Sensitive Information Detection & Masked Logs")
        st.dataframe(pd.DataFrame(sensitive_records))

    with tab4:
        st.subheader("Mandatory 15 Demo IDs Viewer")
        mandatory_ids_input = st.text_input("Enter comma-separated mandatory IDs:", "MSG_001, MSG_002, MSG_003")
        target_ids = [i.strip() for i in mandatory_ids_input.split(",")]

        filtered_cls = [r for r in processed_records if r["message_id"] in target_ids]
        st.json(filtered_cls)

else:
    st.info("Please upload your messages CSV file using the sidebar to run processing.")