# Legal-Doc-AI

<div align="center">

**An AI-powered assistant designed to simplify complex legal and healthcare documents.**

</div>

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Intelligent Document Processing** | Multi-format support (PDF, JPEG, PNG, TXT) with advanced OCR powered by Google Cloud Vision API |
| **Automatic Detection** | Instantly identifies document types: legal contracts, medical reports, insurance policies, or prescriptions |
| **PII Protection** | Enterprise-grade anonymization masking 7 types of PII (Emails, Phones, Aadhaar/ID, Dates, Names, Organizations, Locations) |
| **Deep Analysis & RAG** | Semantic search with FAISS vector storage and Hugging Face CrossEncoder for accurate information retrieval |
| **Multilingual Support** | Results translated into English, Hindi, or Kannada |
| **Plain Language Simplification** | Converts "legalese" and medical jargon into everyday terms |

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Streamlit |
| **AI Models** | Google Gemini Pro, Gemini Vision |
| **Embeddings** | Google Generative AI Embeddings |
| **Vector DB** | FAISS (Facebook AI Similarity Search) |
| **OCR Engine** | Google Cloud Vision API, Pillow |
| **Reranking** | Hugging Face CrossEncoder |
| **Orchestration** | LangChain, Python |

---

## Project Structure

```text
Legal-Doc-AI/
├── src/
│   ├── services/
│   │   ├── ai_processor.py      # Document analysis & simplification logic
│   │   ├── chat_service.py      # Conversational AI with PII protection
│   │   └── rag_service.py       # FAISS vector search & reranking
│   ├── utils/
│   │   ├── document_parser.py   # Multi-layer OCR engine
│   │   ├── pii_anonymizer.py    # Regex-based PII detection
│   │   └── translator.py       # Multilingual support via Gemini
│   └── config.py                # API & PII configuration
├── app.py                       # Main Streamlit UI
├── main.py                      # Core Facade
└── requirements.txt             # Dependency list
```

---

## Getting Started

### 1. Prerequisites
- Python 3.9+
- A Google AI Studio API Key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/ChandanHegde07/Legal-Doc-AI.git
cd Legal-Doc-AI

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY="your_gemini_api_key_here"

# Optional: Path to Google Cloud Service Account JSON for Vision API
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## Use Cases

| Domain | Use Case |
|--------|----------|
| **Legal** | Summarizing Terms of Service (ToS) or identifying hidden "gotcha" clauses in contracts |
| **Healthcare** | Explaining blood test results or medication schedules to patients |
| **Insurance** | Checking if a specific medical procedure is covered under a policy |
| **Privacy-Conscious Users** | Analyzing sensitive data without exposing identity to LLM providers |

---

## Future Scope

- [ ] **Text-to-Speech**: Audio explanations for better accessibility
- [ ] **Expanded Dialects**: Support for more regional Indian languages
- [ ] **ML-based PII**: Moving beyond Regex to Named Entity Recognition (NER) for higher PII accuracy
- [ ] **Contract Comparison**: Side-by-side analysis of two document versions

---

## Authors

| Name | Role |
|------|------|
| [Mukundh R Reddy](https://github.com/) | Ideator & Core Backend |
| [Chandan Hegde](https://github.com/ChandanHegde07) | Frontend & RAG Implementation |
| [Arun Arya](https://github.com/) | Testing & Frontend UI/UX |

---

<div align="center">

**Made for simplifying legal & healthcare documents**

</div>
