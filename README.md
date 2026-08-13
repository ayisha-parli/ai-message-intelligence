# Privacy-Preserving AI Message Intelligence System

An end-to-end, privacy-compliant message processing pipeline designed to classify messages, extract tasks and scheduled events, and mask sensitive information before external processing or logging. Built for real-time local execution using Streamlit, Python, and heuristic extraction engines.

---

## 🛠️ System Architecture & Workflow

1. **Preprocessing & Privacy Masking:** Incoming messages pass through a regex-based redaction filter to intercept credentials, secrets, and personal information before any further handling.
2. **Deterministic Classification:** Redacted messages are routed into six operational categories using local pattern-matching triggers and heuristics.
3. **Task & Event Extraction:** Non-generative entity extraction parses dates, deadlines, times, priorities, and associated individuals without hallucinating missing fields.
4. **Interactive Dashboard:** A Streamlit web interface provides live inspection across all four required operational tabs.

---

## 📋 How Message Classification Works

Messages are categorized into six distinct categories:
- **Action Required:** Triggered by action-oriented keywords, explicit deadlines, or task requests.
- **Meeting or Event:** Triggered by scheduling triggers, meeting platform links, or calendar references.
- **Personal Information:** Triggered by personal contact references or personal details.
- **General Information:** Assigned to purely informational content without explicit action items.
- **Promotional:** Identified via marketing keywords, offers, discounts, or subscription promos.
- **Sensitive Information:** Prioritized when authentication credentials, PINs, or sensitive tokens are detected.

Each output record includes the `message_id`, predicted `category`, a calculated `confidence` score, and a structured `reason` explaining the decision.

---

## 📅 How Tasks and Events are Extracted

Tasks and events are extracted using regex pattern matching and non-generative Named Entity Recognition (NER) heuristics.

### Key Rules:
- **Zero Hallucination Guarantee:** If a date, time, person, or deadline is missing or ambiguous, it is strictly stored as `null` / unresolved.
- **Fields Extracted:** `item_id`, `type` (task or event), `title`, `deadline`, `time`, `person`, `priority` (high/medium), and `source_message_id`.

---

## 🔒 How Sensitive Information is Detected and Masked

The sensitive data detection module scans for high-risk credential types:
- Passwords and Passcodes
- One-Time Passwords (OTPs) and PINs
- Credit Card and Bank details
- Authentication / Bearer Tokens (e.g., GitHub tokens, JWTs)
- Personal Identification numbers (SSN / National IDs)

### Security Safeguards:
- **Dynamic Masking:** Sensitive string values are redacted using asterisk replacement (`*`).
- **Risk Assessment:** Flagged with explicit risk levels (`critical`, `high`, `medium`).
- **Recommended Actions:** Accompanied by local compliance actions such as `do_not_store`, `do_not_send_external`, or `ask_for_confirmation`.
- **Zero Exposure:** Raw sensitive values are prevented from reaching generated logs, screenshots, cloud services, or public repositories.

---

## 💡 Assumptions and Limitations

### Assumptions:
- Input messages are provided in chronological order.
- Standard ISO date patterns (`YYYY-MM-DD`) or standard 12-hour/24-hour time expressions are used for explicit date extraction.

### Limitations:
- **Relative Temporal Expressions:** Unstructured expressions like "next Tuesday" require anchor execution timestamps to resolve to explicit calendar dates.
- **Conversational Nuance:** Highly informal meeting requests without explicit keywords or timestamps may be classified as general information to avoid false positives.

---

## 🤖 AI-Tool Usage Declaration

AI development assistance tools were utilized during development for code structure generation, documentation formatting, and boilerplate setup. All core processing logic, regex pattern implementations, and pipeline integrations were reviewed and validated locally.

---

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ayisha-parli/ai-message-intelligence.git](https://github.com/ayisha-parli/ai-message-intelligence.git)
   cd ai-message-intelligence
