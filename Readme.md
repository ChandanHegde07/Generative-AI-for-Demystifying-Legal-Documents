# Generative AI for Demystifying Healthcare Documents

This project is an AI-powered assistant designed to simplify and analyze complex healthcare documents such as **insurance policies, medical reports, and prescriptions**. Built with **Google Gemini API** and an interactive **Streamlit interface**, it helps patients, caregivers, and healthcare professionals better understand critical documents by extracting key details, identifying potential risks, and providing plain-language explanations.

---

## Features
- **PDF, JPEG, PNG Upload** – Upload one or more healthcare documents in PDF, JPEG, or PNG format (insurance, prescriptions, medical reports, etc.).
- **Advanced OCR Technology** – Uses **Google Cloud Vision API** for accurate text extraction from images, with intelligent fallback to Pillow+Gemini for maximum reliability.
- **PII Protection** – Automatically detects and anonymizes **7 types of Personally Identifiable Information** (emails, phone numbers, ID/Aadhaar numbers, dates, names, organizations, locations) before sending to AI, then restores real data in outputs for privacy protection.
- **AI-Powered Medical Analysis** – Automatically detects the type of healthcare document and extracts essential information using Gemini, with special focus on medical, insurance, and patient details.
- **Contextual Q&A** – Ask natural language questions about your healthcare document and receive detailed AI-generated answers for patients and caregivers.
- **Simplification & Summarization** – Converts medical, insurance, or technical jargon into clear, easy-to-understand language for patients and families.
- **Risk & Compliance Insights** – Identifies potential gaps in insurance coverage, medical risks, deadlines, or compliance requirements for healthcare documents.
- **Multilingual Support** – Translate results into **English, Hindi, or Kannada** for accessibility in healthcare settings.
- **Interactive Web UI** – Streamlit-based interface for a user-friendly experience.

---

## Tech Stack
- **Streamlit** – Frontend web framework for interactive UI.
- **Python** – Core application logic and integrations.
- **Google Gemini API** – For all AI-powered document analysis and Q&A.
- **Google Cloud Vision API** – Advanced OCR for text extraction from images (with Pillow+Gemini fallback).
- **PIIAnonymizer** – Custom regex-based PII detection and anonymization engine.

---

## Demo

### Step-by-Step Flow
1. **Upload Document** → Drag and drop PDFs, JPEGs, or PNGs (insurance policies, medical reports, prescriptions, etc.).
2. **AI Medical Analysis** → The system detects the healthcare document type and extracts key data (e.g., policy details, medical parameters, claim eligibility, patient information).
3. **Simplification & Summarization** → Converts complex medical or insurance language into simple, everyday English, Hindi, or Kannada for patients and families.
4. **Interactive Q&A** → Users ask custom questions, like *“Does this policy cover hospitalization for cardiac surgery?”* or *“What are the exclusions in this insurance?”*
5. **Risk & Compliance Alerts** → Highlights possible gaps in coverage, claim deadlines, medical alerts, or compliance risks.
6. **Multilingual Translation** → Outputs available in **English, Hindi, or Kannada**.

---



## Use Cases
- Helping patients and families understand insurance policies (coverage, exclusions, claim procedures).
- Simplifying **medical reports or prescriptions** into everyday language for healthcare decisions.
- **Privacy-first document processing** – Protecting sensitive patient information (PII) from AI models while maintaining readable outputs.
- Identifying **potential risks** or deadlines in healthcare documents (insurance, medical).
- Providing **regional language support** for patients, caregivers, and healthcare professionals.
- **Accurate OCR** for scanned medical documents, insurance forms, and handwritten prescriptions.

---

## Future Scope
Potential future enhancements:
- **Text-to-Speech Support** – For accessibility, especially in healthcare settings.
- **Expanded Language Coverage** – Support for more Indian languages for healthcare documents.
- **Enhanced PII Detection** – Machine learning-based PII detection for better accuracy.
- **Analytics Dashboard** – Visual insights into healthcare document types, risks, and insurance claim patterns.

---
## Project Structure

- `.env`: Stores environment variables like `GEMINI_API_KEY`.
- `app.py`: The main Streamlit application script.
- `main.py`: Facade for core functions, using Gemini for all document analysis and Q&A.
- `requirements.txt`: Lists all Python dependencies.
- `src/`: Contains the core logic, organized into sub-packages:
    - `config.py`: Handles API key and Gemini model configuration, PII settings, and Cloud Vision initialization.
    - `utils/`:
        - `document_parser.py`: Extracts text from PDFs and images using Cloud Vision API with Pillow+Gemini fallback.
        - `pii_anonymizer.py`: **NEW** - Detects and anonymizes 7 types of PII (email, phone, ID/Aadhaar, dates, names, organizations, locations).
        - `helpers.py`: General utility functions.
        - `translator.py`: Handles text translation using Gemini.
    - `services/`:
        - `ai_processor.py`: Implements AI-powered document analysis with PII anonymization (entity extraction, summarization, risk assessment, document type detection, complex terms explanation, compliance checklist, simplification).
        - `chat_service.py`: Service for conversational AI interactions with dual-context PII protection.

---

## Privacy & Security Features

###  PII Anonymization
This application implements **enterprise-grade PII protection** to safeguard sensitive patient information:

- **Automatic Detection**: Identifies 7 types of PII:
  - Email addresses
  - Phone numbers (Indian & international formats)
  - ID/Aadhaar numbers (12-digit)
  - Dates (multiple formats)
  - Person names
  - Organizations
  - Geographic locations

- **Privacy-First Processing**:
  1. Extract text with original PII intact
  2. **Anonymize** before sending to Gemini AI (PII replaced with placeholders)
  3. Process document with AI (AI never sees real PII)
  4. **Deanonymize** responses before showing to users
  5. Users see real, readable data in outputs

- **Benefits**:
  -  **Privacy**: Patient data protected from AI models
  -  **User Experience**: Professional, readable outputs (no placeholders)
  -  **Security**: PII mappings stored in-memory only, cleared per session
  -  **Compliance**: Helps meet healthcare data protection requirements

###  Advanced OCR Technology
Multi-layer OCR system for maximum text extraction accuracy:

1. **Primary**: Google Cloud Vision API (highly accurate, free tier: 1000 requests/month)
2. **Fallback**: Pillow + Gemini AI (when Vision API unavailable)
3. **Intelligent Routing**: Automatically selects best method based on availability

**Supported formats**: PDF (text + scanned), JPEG, PNG, GIF

---

## Setup and Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ChandanHegde07/Generative-AI-for-Demystifying-Legal-Documents.git
    cd Generative-AI-for-Demystifying-Legal-Documents
    ```
2. **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # Or use: source venv/bin/activate  # On Mac/Linux
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Configure API Key:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    
    **Optional - Enable Google Cloud Vision API (for better OCR):**
    - Create a Google Cloud project and enable Vision API
    - Download service account JSON key
    - Set environment variable:
      ```
      GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
      ```
    - Or the app will use the same `GOOGLE_API_KEY` for Vision API
    - If Vision API is unavailable, the app automatically falls back to Pillow+Gemini

5. **Configure PII Protection (Optional):**
    In `src/config.py`, you can customize PII settings:
    ```python
    ENABLE_PII_ANONYMIZATION: bool = True   # Toggle PII protection
    SHOW_PII_MAPPING: bool = True           # Show PII mapping to users
    ```

6. **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

## Authors
- **Mukundh R Reddy** – Ideator & Core Backend
- **Chandan Hegde** - Frontend & RAG Implementation
- **Arun Arya** - Testing & Frontend Improvements

## License

This project is licensed under the [MIT License](./LICENSE) - see the LICENSE file for details.

