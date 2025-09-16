# Generative AI for Demystifying Healthcare Documents

This project is an AI-powered assistant designed to simplify and analyze complex healthcare-related documents such as **insurance policies, medical reports, prescriptions, and government health schemes** in India. Built with **Google Gemini API** and an interactive **Streamlit interface**, it helps patients, caregivers, and healthcare professionals better understand critical documents by extracting key details, identifying potential risks, and providing plain-language explanations.

---

## Features
- **PDF Upload** – Upload one or more healthcare documents in PDF format (insurance, prescriptions, lab reports).  
- **AI-Powered Analysis** – Automatically detects the type of document and extracts essential information.  
- **Contextual Q&A** – Ask natural language questions about your document and receive detailed AI-generated answers.  
- **Simplification & Summarization** – Converts medical, technical, or legal jargon into clear, easy-to-understand language.  
- **Risk & Compliance Insights** – Identifies potential gaps in insurance coverage, critical medical concerns, or deadlines for claims/renewals.  
- **Multilingual Support** – Translate results into **English, Hindi, or Kannada** to improve accessibility for diverse Indian patient populations.  
- **Interactive Web UI** – Streamlit-based interface for a user-friendly experience.  

---

## Tech Stack
- **Google Gemini API** – Generative AI model for healthcare document understanding.  
- **Google Cloud Vision** – OCR support for scanned or handwritten medical PDFs.  
- **Google Cloud Translate** – Multilingual translation capabilities, including major Indian languages.  
- **Streamlit** – Frontend web framework for interactive UI.  
- **Python** – Core application logic and integrations.  

---

## Demo

### Step-by-Step Flow
1. **Upload Document** → Drag and drop PDFs such as **insurance policies, prescriptions, lab reports, or government scheme documents**.  
2. **AI Analysis** → The system detects the document type and extracts key data (e.g., policy details, medical parameters, claim eligibility).  
3. **Simplification & Summarization** → Converts complex medical or policy language into simple, everyday Indian English or regional language.  
4. **Interactive Q&A** → Users ask custom questions, like *“Does this policy cover hospitalization for cardiac surgery?”*  
5. **Risk & Compliance Alerts** → Highlights possible gaps, claim deadlines, or medical alerts.  
6. **Multilingual Translation** → Outputs available in **English, Hindi, or Kannada**.    
---

## Use Cases 
- Helping patients understand insurance policies (coverage, exclusions, claim procedures).
- Simplifying **medical reports or prescriptions** into everyday language.
- Identifying **potential risks** or deadlines in healthcare documents.  
- Providing **regional language support** for patients and families.  

---

## Future Scope 
With more time, the project could expand to include:    
- **Text-to-Speech Support** – Especially for rural or elderly patients with low literacy.  
- **Expanded Language Coverage** – Support for **Marathi, Tamil, Telugu, Bengali**, etc.   
- **Privacy & Security Enhancements** – HIPAA-like compliance adapted to Indian healthcare data norms.  
- **Analytics Dashboard** – Visual insights into common illnesses, hospital visits, and insurance claim patterns in India.  

---
## Project Structure

-   `.env`: Stores environment variables like `GOOGLE_API_KEY`.
-   `app.py`: The main Streamlit application script (remains unchanged from your original).
-   `main.py`: Acts as a facade, importing and re-exporting core functions from the `src/` directory to maintain compatibility with `app.py`.
-   `requirements.txt`: Lists all Python dependencies.
-   `src/`: Contains the core logic, organized into sub-packages:
    -   `config.py`: Handles API key loading, Gemini model initialization, and optional Google Cloud Vision/Translate client setup.
    -   `utils/`:
        -   `document_parser.py`: Functions for extracting text from various file formats, including OCR fallback.
        -   `helpers.py`: General utility functions (e.g., `is_meaningful_content`).
        -   `translator.py`: Handles text translation using Gemini (and optionally Google Cloud Translate).
    -   `services/`:
        -   `ai_processor.py`: Implements all the AI-powered document analysis functions (e.g., entity extraction, summarization, risk assessment, document type detection, complex terms explanation, compliance checklist, simplification).
        -   `chat_service.py`: Dedicated service for handling conversational AI interactions (`ask_gemini`).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ChandanHegde07/Generative-AI-for-Demystifying-Legal-Documents.git
    cd Generative-AI-for-Demystifying-Legal-Documents
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you plan to use Google Cloud Vision/Translate for OCR, uncomment `google-cloud-vision` and `google-cloud-translate` in `requirements.txt` and install them. You will also need to set up Google Cloud credentials for these services.)*
4.  **Configure API Key:**
    Create a `.env` file in the root directory (`https://github.com/ChandanHegde07/Generative-AI-for-Demystifying-Legal-Documents.git/.env`) and add your Google Gemini API key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    If using Google Cloud Vision/Translate, also set up your Google Application Credentials:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service_account_key.json"
    ```
5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

## Usage

1.  Upload one or more legal documents (PDF, JPG, PNG).
2.  Select the desired language for AI responses.
3.  Interact with the document through various tabs:
    -   **Document View**: See the extracted text.
    -   **Actions**: Perform specific analyses like key entity extraction, risk assessment, summarization, etc.
    -   **Ask AI**: Chat with the AI assistant about your document.

## Authors
- **Mukundh R Reddy**  
- **Chandan Hegde**
