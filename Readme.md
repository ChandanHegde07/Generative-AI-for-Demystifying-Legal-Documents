# Generative AI for Healthcare Docs

<div align="center">

**An AI-powered assistant designed to simplify complex legal and healthcare documents.**

</div>

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Intelligent Document Processing** | Multi-format support with advanced OCR powered by Google Cloud Vision API |
| **Automatic Detection** | Instantly identifies document types: legal, medical, insurance, or prescriptions |
| **PII Protection** | Enterprise-grade anonymization masking 7 types of PII |
| **Deep Analysis & RAG** | Semantic search with FAISS vector storage and Hugging Face CrossEncoder |
| **Multilingual Support** | Results translated into English, Hindi, or Kannada |
| **Plain Language Simplification** | Converts "legalese" and medical jargon into everyday terms |

---

## Supported Document Types

| Document Type | Formats | Description |
|--------------|---------|-------------|
| Legal Contracts | PDF, TXT | Contracts, agreements, terms of service, legal notices |
| Medical Reports | PDF, JPEG, PNG | Lab reports, diagnostic results, medical records |
| Insurance Policies | PDF, TXT | Health insurance, life insurance, claim documents |
| Prescriptions | PDF, JPEG, PNG | Medical prescriptions, medication schedules |

---

## PII Types Masked

| PII Type | Example | Masking Method |
|----------|---------|----------------|
| Email Addresses | user@example.com | [EMAIL_REDACTED] |
| Phone Numbers | +91-9876543210 | [PHONE_REDACTED] |
| Aadhaar/ID Numbers | 1234-5678-9012 | [ID_REDACTED] |
| Dates | 15/08/2024 | [DATE_REDACTED] |
| Names | John Doe | [NAME_REDACTED] |
| Organizations | ABC Corp | [ORG_REDACTED] |
| Locations | Bangalore, India | [LOCATION_REDACTED] |

---

## Supported Languages

| Language | Code | Status |
|----------|------|--------|
| English | en | Fully Supported |
| Hindi | hi | Fully Supported |
| Kannada | kn | Fully Supported |

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | Latest | Web UI Framework |
| AI Models | Google Gemini Pro | 1.5 Pro | Text Processing |
| AI Models | Gemini Vision | 1.5 Pro | Image/Document Analysis |
| Embeddings | Google Generative AI | Latest | Vector Embeddings |
| Vector Database | FAISS | Latest | Similarity Search |
| OCR | Google Cloud Vision | Latest | Document OCR |
| OCR | Pillow | Latest | Image Processing |
| Reranking | Hugging Face CrossEncoder | Latest | Document Reranking |
| Orchestration | LangChain | Latest | LLM Chain Management |
| Backend | Python | 3.9+ | Core Runtime |

---

## Project Structure

| Directory/File | Purpose |
|----------------|---------|
| `src/services/ai_processor.py` | Document analysis and simplification logic |
| `src/services/chat_service.py` | Conversational AI with PII protection |
| `src/services/rag_service.py` | FAISS vector search and reranking |
| `src/utils/document_parser.py` | Multi-layer OCR engine |
| `src/utils/pii_anonymizer.py` | Regex-based PII detection |
| `src/utils/translator.py` | Multilingual support via Gemini |
| `src/config.py` | API and PII configuration |
| `app.py` | Main Streamlit UI application |
| `main.py` | Core Facade for orchestration |
| `requirements.txt` | Dependency list |

---

## API Configuration

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | Yes | Google AI Studio API key for Gemini models | None |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to Google Cloud Service Account JSON | None |

---

## Getting Started

### Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| Python | 3.9+ | Core programming language |
| pip | Latest | Package installer |
| Git | Latest | Version control |
| Google AI Studio Account | - | API key provider |

### Installation

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

### Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY="your_gemini_api_key_here"
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Run the App

```bash
streamlit run app.py
```

---

## Use Cases

| Domain | Use Case | Input Format | Output |
|--------|----------|--------------|--------|
| Legal | Summarize Terms of Service | PDF/TXT | Plain English Summary |
| Legal | Identify Hidden Clauses | PDF/TXT | Risk Assessment Report |
| Healthcare | Explain Blood Test Results | PDF/Image | Patient-Friendly Report |
| Healthcare | Medication Schedules | PDF/Image | Simplified Schedule |
| Insurance | Coverage Check | PDF/TXT | Coverage Summary |
| Privacy | Analyze Sensitive Data | Any | Redacted Analysis |

---

## Model Capabilities

| Capability | Model Used | Accuracy |
|------------|-----------|----------|
| Text Summarization | Gemini Pro | High |
| Document OCR | Google Cloud Vision | Very High |
| Image Analysis | Gemini Vision | High |
| Semantic Search | FAISS + Embeddings | High |
| Reranking | CrossEncoder | Very High |
| Translation | Gemini Pro | High |
| PII Detection | Regex + Rules | High |

---

## Future Scope

| Feature | Priority | Description |
|---------|----------|-------------|
| Text-to-Speech | Medium | Audio explanations for accessibility |
| Expanded Dialects | Medium | Support for more Indian languages |
| ML-based PII | High | NER-based PII detection |
| Contract Comparison | Low | Side-by-side document analysis |
| Multi-document Analysis | Medium | Compare multiple documents |
| Custom Templates | Low | Industry-specific templates |

---

## Authors

| Name | Role | GitHub | Contributions |
|------|------|--------|---------------|
| Mukundh R Reddy | Ideator & Core Backend | [GitHub](https://github.com/mukundhr) | Architecture, Backend, RAG |
| Chandan Hegde | Frontend & RAG Implementation | [GitHub](https://github.com/ChandanHegde07) | UI/UX, Frontend, Integration |
| Arun Arya | Testing & Frontend UI/UX | [GitHub](https://github.com/ArunArya-01) | Testing, UI/UX Design |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made for simplifying legal & healthcare documents**

</div>
