# Reverse Template UX Guidelines

## Concept
The "Reverse Template" workflow flips the traditional EHR data entry model. Instead of forcing the doctor to navigate multiple tabs and fill specific form fields (Chief Complaint, HPI, Exam, etc.), the doctor provides a single, continuous narrative (via voice or text). The system then uses NLP to "reverse engineer" the structured data from this narrative.

## Workflow

1.  **Dictation / Free Text Entry**
    *   Doctor opens the "Medical Note" page.
    *   Uses the **Voice Input** (microphone) to dictate the entire visit note in one go.
    *   **Technology**: Uses **VOSK** for offline speech recognition (works on old PCs).
    *   *Example:* "Patient presents with 3 weeks of morning stiffness. Left knee is swollen and tender. Starting Methotrexate 15mg."

2.  **Processing (The "Reverse" Step)**
    *   Doctor clicks **"Generate Report"**.
    *   Frontend sends the raw text to the backend (`/api/v1/process-medical-note`).
    *   Backend NLP (spaCy) extracts entities:
        *   **Symptoms** -> Chief Complaint / HPI
        *   **Anatomy/Conditions** -> Physical Exam / Assessment
        *   **Medications** -> Plan / Meds List

3.  **Review & Confirmation**
    *   System displays a **Split View**:
        *   **Left**: Original Note (editable).
        *   **Right**: Extracted Structured Data (Review Panel).
    *   Doctor reviews the extracted fields.
    *   Confidence scores (if available) highlight uncertain extractions.

4.  **Finalization**
    *   Doctor clicks **"Save & Finalize"**.
    *   Structured data is saved to the database (LLBLGen entities).
    *   Original note is preserved as the "source of truth".

## UI Components

### 1. Medical Note Input
*   Large Textarea.
*   Prominent "Dictate" button.
*   "Generate Report" action button.

### 2. Extraction Review Panel
*   Displays extracted entities grouped by category.
*   Allows quick corrections (e.g., "Remove this medication", "Change status").

## Benefits for Rural Context
*   **Speed**: Dictating is faster than clicking through 7 tabs.
*   **Resilience**: Works offline (if local NLP is used) or with slow connections (text upload is small).
*   **Simplicity**: Minimal training required; mimics paper charting workflow.
