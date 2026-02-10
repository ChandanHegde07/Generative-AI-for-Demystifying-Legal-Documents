<h1 style="color: #2E86AB; text-align: center;">Generative AI for Healthcare Docs</h1>

<div align="center">

<span style="background-color: #28A745; color: white; padding: 5px 15px; border-radius: 20px;">MIT License</span>
<span style="background-color: #3776AB; color: white; padding: 5px 15px; border-radius: 20px;">Python 3.9+</span>
<span style="background-color: #FF4B4B; color: white; padding: 5px 15px; border-radius: 20px;">Streamlit</span>

**<span style="color: #6C757D;">An AI-powered assistant designed to simplify complex legal and healthcare documents.</span>**

</div>

---

## <span style="color: #E94F37;">Key Features</span>

| <span style="color: #2E86AB;">Feature</span> | <span style="color: #2E86AB;">Description</span> |
|:---|:---|
| <span style="color: #28A745;">**Intelligent Document Processing**</span> | Multi-format support (PDF, JPEG, PNG, TXT) with advanced OCR powered by Google Cloud Vision API |
| <span style="color: #28A745;">**Automatic Detection**</span> | Instantly identifies document types: legal contracts, medical reports, insurance policies, or prescriptions |
| <span style="color: #DC3545;">**PII Protection**</span> | Enterprise-grade anonymization masking 7 types of PII (Emails, Phones, Aadhaar/ID, Dates, Names, Organizations, Locations) |
| <span style="color: #17A2B8;">**Deep Analysis & RAG**</span> | Semantic search with FAISS vector storage and Hugging Face CrossEncoder for accurate information retrieval |
| <span style="color: #FFC107;">**Multilingual Support**</span> | Results translated into English, Hindi, or Kannada |
| <span style="color: #6F42C1;">**Plain Language Simplification**</span> | Converts "legalese" and medical jargon into everyday terms |

---

## <span style="color: #FD7E14;">Tech Stack</span>

| <span style="color: #2E86AB;">Layer</span> | <span style="color: #2E86AB;">Technologies</span> |
|:---|:---|
| <span style="color: #E94F37;">**Frontend**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">Streamlit</span> |
| <span style="color: #E94F37;">**AI Models**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">Google Gemini Pro, Gemini Vision</span> |
| <span style="color: #E94F37;">**Embeddings**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">Google Generative AI Embeddings</span> |
| <span style="color: #E94F37;">**Vector DB**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">FAISS (Facebook AI Similarity Search)</span> |
| <span style="color: #E94F37;">**OCR Engine**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">Google Cloud Vision API, Pillow</span> |
| <span style="color: #E94F37;">**Reranking**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">Hugging Face CrossEncoder</span> |
| <span style="color: #E94F37;">**Orchestration**</span> | <span style="background-color: #F8F9FA; padding: 2px 8px; border-radius: 4px;">LangChain, Python</span> |

---

## <span style="color: #20C997;">Project Structure</span>

```text
<span style="color: #6C757D;">Legal-Doc-AI/
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

## <span style="color: #28A745;">Getting Started</span>

### <span style="color: #2E86AB;">1. Prerequisites</span>

- <span style="color: #3776AB;">**Python 3.9+**</span>
- <span style="color: #F7DF1E;">**A Google AI Studio API Key**</span>

### <span style="color: #2E86AB;">2. Installation</span>

```bash
<span style="color: #6C757D;"># Clone the repository</span>
git clone https://github.com/ChandanHegde07/Legal-Doc-AI.git
cd Legal-Doc-AI

<span style="color: #6C757D;"># Setup virtual environment</span>
python -m venv venv
source venv/bin/activate  <span style="color: #6C757D;"># On Windows: venv\Scripts\activate</span>

<span style="color: #6C757D;"># Install dependencies</span>
pip install -r requirements.txt
```

### <span style="color: #2E86AB;">3. Configuration</span>

Create a `.env` file in the root directory:

```env
<span style="color: #28A745;">GOOGLE_API_KEY</span>="your_gemini_api_key_here"

<span style="color: #6C757D;"># Optional: Path to Google Cloud Service Account JSON for Vision API</span>
<span style="color: #28A745;">GOOGLE_APPLICATION_CREDENTIALS</span>="path/to/service-account.json"
```

### ▶<span style="color: #2E86AB;">4. Run the App</span>

```bash
streamlit run app.py
```

---

## <span style="color: #E94F37;">Use Cases</span>

| <span style="color: #2E86AB;">Domain</span> | <span style="color: #2E86AB;">Use Case</span> |
|:---|:---|
| <span style="color: #E94F37;">**Legal**</span> | Summarizing Terms of Service (ToS) or identifying hidden "gotcha" clauses in contracts |
| <span style="color: #DC3545;">**Healthcare**</span> | Explaining blood test results or medication schedules to patients |
| <span style="color: #17A2B8;">**Insurance**</span> | Checking if a specific medical procedure is covered under a policy |
| <span style="color: #6F42C1;">**Privacy-Conscious Users**</span> | Analyzing sensitive data without exposing identity to LLM providers |

---

## <span style="color: #FD7E14;">Future Scope</span>

- [ ] <span style="color: #28A745;">**Text-to-Speech**</span>: Audio explanations for better accessibility
- [ ] <span style="color: #28A745;">**Expanded Dialects**</span>: Support for more regional Indian languages
- [ ] <span style="color: #28A745;">**ML-based PII**</span>: Moving beyond Regex to Named Entity Recognition (NER) for higher PII accuracy
- [ ] <span style="color: #28A745;">**Contract Comparison**</span>: Side-by-side analysis of two document versions

---

## <span style="color: #20C997;">Authors</span>

| <span style="color: #2E86AB;">Name</span> | <span style="color: #2E86AB;">Role</span> |
|:---|:---|
| [Mukundh R Reddy](https://github.com/mukundhr) | <span style="color: #6C757D;">Ideator & Core Backend</span> |
| [Chandan Hegde](https://github.com/ChandanHegde07) | <span style="color: #6C757D;">Frontend & RAG Implementation</span> |
| [Arun Arya](https://github.com/ArunArya-01) | <span style="color: #6C757D;">Testing & Frontend UI/UX</span> |

---

<div align="center">

<span style="background: linear-gradient(90deg, #E94F37, #2E86AB, #28A745, #FD7E14); color: white; padding: 10px 30px; border-radius: 25px; font-weight: bold;">
Made for simplifying legal & healthcare documents
</span>

</div>
