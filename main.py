import os
from dotenv import load_dotenv
from typing import List, Any 

from src.config import Config
from src.services.ai_processor import AIProcessor
from src.services.chat_service import ChatService
from src.utils.document_parser import DocumentParser
from src.utils.translator import GeminiTranslator

load_dotenv()

def main_workflow(uploaded_files: List[Any], user_question: str = "What are the main obligations?", target_lang: str = "English"):
    print("--- Initializing Services ---")
    doc_parser = DocumentParser()
    ai_processor = AIProcessor()
    chat_service = ChatService()
    translator = GeminiTranslator() 

    print("\n--- Extracting Text ---")
    if not uploaded_files:
        print("No files uploaded. Exiting.")
        return
    
    document_text = doc_parser.extract_from_multiple_files(uploaded_files)
    processed_text = doc_parser.preprocess_text(document_text)
    
    is_valid, validation_msg = doc_parser.validate_extracted_text(processed_text)
    if not is_valid:
        print(f"Document validation failed: {validation_msg}")
        return

    print("\n--- Classifying Document ---")
    classification_result = ai_processor.classify_document(processed_text)
    doc_type = classification_result.get("document_type", "Other Legal Document")
    print(f"Detected Document Type: {doc_type} (Confidence: {classification_result.get('confidence')})")

    chat_service.set_document_context(processed_text, doc_type)

    print(f"\n--- Answering Question in {target_lang} ---")
    answer = chat_service.ask_question(user_question, language=target_lang)
    print(f"Q: {user_question}\nA: {answer}")

    print("\n--- Generating Summary (Example) ---")
    summary = ai_processor.summarize_document(processed_text, doc_type, language=target_lang)
    print(f"Summary:\n{summary[:500]}...")

if __name__ == "__main__":
    class MockUploadedFile:
        def __init__(self, name, type, content):
            self.name = name
            self.type = type
            self._content = content
        def getvalue(self):
            return self._content.encode('utf-8') if isinstance(self._content, str) and self.type == "text/plain" else self._content

    dummy_text_content = "This is a legally binding agreement made on 15th September 2023 between Party A and Party B. Party A shall pay $1000 by 1st October 2023. This agreement is governed by the laws of California."
    
    dummy_text_file = MockUploadedFile(
        "sample_agreement.txt",
        "text/plain",
        dummy_text_content
    )
    
    mock_uploaded_files = [dummy_text_file] 

    main_workflow(mock_uploaded_files, user_question="What is the payment amount and due date?", target_lang="English")