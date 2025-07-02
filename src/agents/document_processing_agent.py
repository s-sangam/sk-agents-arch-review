# src/agents/document_processing_agent.py
import os
import base64
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.prompt_template import PromptTemplate

class DocumentProcessingAgent(Agent):
    def __init__(self, kernel: sk.Kernel, service_id: str): # Service ID is now passed
        super().__init__(
            kernel=kernel,
            service_id=service_id, # Use the passed service ID
            name="DocumentProcessor",
            description="Agent specialized in processing documents to extract text and comprehend images.",
            instructions=(
                "You are an expert document processor. Your task is to extract all relevant text "
                "from a given document and to generate descriptions of any images present. "
                "You will then synthesize this information into a comprehensive summary, "
                "highlighting key aspects of the design proposal."
            )
        )
        self._doc_parser = kernel.plugins["DocParser"]
        self._image_intel = kernel.plugins["ImageIntel"]
        self._llm = kernel.get_service(service_id) # Get the specific LLM service

    @kernel_function(
        description="Processes a document to extract its full text, comprehend images, and generate a comprehensive summary.",
        name="ProcessDocumentAndSummarize",
        input_description="The file path of the document (PDF, Word, etc.) to process."
    )
    async def process_document(self, file_path: str) -> str:
        print(f"[DocumentProcessor] Processing document: {file_path}")

        # 1. Extract text content
        document_text = await self._doc_parser.invoke("ExtractDocumentText", sk.KernelArguments(document_path=file_path))
        print(f"[DocumentProcessor] Extracted text content length: {len(document_text)}")

        # 2. Comprehend images (assuming image extraction logic from document_parsing_plugin could provide base64 images)
        # For this prototype, we'll simulate image processing as extract_document_text doesn't return image data directly.
        # In a real scenario, Document Intelligence could extract images or you'd use a separate image extraction step.
        image_summary = ""
        # The ImageComprehensionPlugin uses its own service_id set in main.py, which is the complex LLM.
        # So no explicit service_id needed here for image_intel.invoke

        # 3. Summarize using LLM (using the fast_llm service)
        prompt_template = PromptTemplate(
            template=(
                "You are an expert document summarizer. Summarize the following document content "
                "into a comprehensive, concise, and professional design proposal summary. "
                "Highlight the main components, proposed architecture, key features, and any "
                "dependencies or external integrations mentioned. Focus on technical details relevant to an architecture review.\n\n"
                "Document Content:\n{{"
                "$"
                "input}}\n\n"
                "Comprehensive Design Proposal Summary:"
            ),
            prompt_template_config=PromptTemplateConfig(
                input_variables=[sk.semantickernel.input_variable.InputVariable(name="input", description="The document content to summarize.")],
                execution_settings=self._llm.get_prompt_execution_settings(service_id=self.service_id, max_tokens=1000, temperature=0.2)
            )
        )
        
        # Ensure the LLM service used here is self._llm, which corresponds to fast_llm
        response = await self._llm.get_chat_message_content(
            messages=full_content_to_summarize,
            prompt_template=prompt_template,
            kernel=self._kernel 
        )
        
        comprehensive_summary = response.content
        print("[DocumentProcessor] Document summarized successfully.")
        return comprehensive_summary