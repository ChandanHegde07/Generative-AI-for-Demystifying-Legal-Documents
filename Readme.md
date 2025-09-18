# Generative AI for Demystifying Healthcare Documents

This project is an AI-powered assistant designed to simplify and analyze complex healthcare documents such as **insurance policies, medical reports, and prescriptions**. Built with **Google Gemini API** and an interactive **Streamlit interface**, it helps patients, caregivers, and healthcare professionals better understand critical documents by extracting key details, identifying potential risks, and providing plain-language explanations.

---

## Features
- **PDF, JPEG, PNG Upload** – Upload one or more healthcare documents in PDF, JPEG, or PNG format (insurance, prescriptions, medical reports, etc.).
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
- Identifying **potential risks** or deadlines in healthcare documents (insurance, medical).
- Providing **regional language support** for patients, caregivers, and healthcare professionals.

---



## Future Scope
Potential future enhancements:
- **Text-to-Speech Support** – For accessibility, especially in healthcare settings.
- **Expanded Language Coverage** – Support for more Indian languages for healthcare documents.
- **Privacy & Security Enhancements** – Improved data protection for sensitive medical information.
- **Analytics Dashboard** – Visual insights into healthcare document types, risks, and insurance claim patterns.

---
## Project Structure

- `.env`: Stores environment variables like `GEMINI_API_KEY`.
- `app.py`: The main Streamlit application script.
- `main.py`: Facade for core functions, using Gemini for all document analysis and Q&A.
- `requirements.txt`: Lists all Python dependencies.
- `src/`: Contains the core logic, organized into sub-packages:
    - `config.py`: Handles API key and Gemini model configuration.
    - `utils/`:
        - `document_parser.py`: Extracts text from PDFs (images are handled by Gemini Vision in `main.py`).
        - `helpers.py`: General utility functions.
        - `translator.py`: Handles text translation using Gemini.
    - `services/`:
        - `ai_processor.py`: Implements AI-powered document analysis functions (entity extraction, summarization, risk assessment, document type detection, complex terms explanation, compliance checklist, simplification).
        - `chat_service.py`: Service for conversational AI interactions (`ask_gemini`).

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
    GOOGLE_API_KEY="GOOGLE_API_KEY HERE"
    ```
5. **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

## Authors
- **Mukundh R Reddy**
- **Chandan Hegde**
