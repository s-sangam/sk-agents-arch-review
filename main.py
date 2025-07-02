# main.py
import asyncio
import os
import json
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planners.sequential_planner import SequentialPlanner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Agents
from src.agents.document_processing_agent import DocumentProcessingAgent
from src.agents.structure_validator_agent import StructureValidatorAgent
from src.agents.security_architect_agent import SecurityArchitectAgent
from src.agents.lead_reviewer_agent import LeadReviewerAgent

# Import Plugins
from src.plugins.document_parsing_plugin import DocumentParsingPlugin
from src.plugins.image_comprehension_plugin import ImageComprehensionPlugin
from src.plugins.local_rule_loader_plugin import LocalRuleLoaderPlugin

async def main():
    print("🚀 Starting Architecture Review Orchestrator...")

    # --- Configuration ---
    # For GPT-3.5-turbo / fast text tasks
    AZURE_OPENAI_ENDPOINT_FAST = os.getenv("AZURE_OPENAI_ENDPOINT_FAST")
    AZURE_OPENAI_API_KEY_FAST = os.getenv("AZURE_OPENAI_API_KEY_FAST")
    AZURE_OPENAI_DEPLOYMENT_NAME_FAST = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_FAST")       

    # For GPT-4o / complex tasks
    AZURE_OPENAI_ENDPOINT_COMPLEX = os.getenv("AZURE_OPENAI_ENDPOINT_COMPLEX")
    AZURE_OPENAI_API_KEY_COMPLEX = os.getenv("AZURE_OPENAI_API_KEY_COMPLEX")
    AZURE_OPENAI_DEPLOYMENT_NAME_COMPLEX = os.getenv("AZURE_DEPLOYMENT_NAME_COMPLEX") 
    
    # for Doc Intelligence service
    AZURE_DOC_INTEL_ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
    AZURE_DOC_INTEL_API_KEY = os.getenv("AZURE_DOC_INTEL_API_KEY")

    

    if not all([AZURE_OPENAI_ENDPOINT_FAST, AZURE_OPENAI_API_KEY_FAST, AZURE_OPENAI_DEPLOYMENT_NAME_FAST, AZURE_OPENAI_DEPLOYMENT_NAME_COMPLEX, 
                AZURE_OPENAI_ENDPOINT_COMPLEX, AZURE_OPENAI_API_KEY_COMPLEX, AZURE_DOC_INTEL_ENDPOINT, AZURE_DOC_INTEL_API_KEY]):
        print("Error: Missing one or more environment variables. Please check your .env file.")
        return

    # --- Initialize Semantic Kernel ---
    kernel = sk.Kernel()

    # Add Azure OpenAI Chat Completion services with distinct IDs
    print("🛠️ Initializing and adding LLM services...")
    complex_llm_service_id = "complex_llm"
    fast_llm_service_id = "fast_llm"

    kernel.add_service(
        AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME_COMPLEX,
            endpoint=AZURE_OPENAI_ENDPOINT_COMPLEX,
            api_key=AZURE_OPENAI_API_KEY_COMPLEX,
            service_id=complex_llm_service_id # Service for complex tasks / vision
        ),
    )
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME_FAST,
            endpoint=AZURE_OPENAI_ENDPOINT_FAST,
            api_key=AZURE_OPENAI_API_KEY_FAST,
            service_id=fast_llm_service_id # Service for fast text-only tasks
        ),
    )
    print("✅ LLM services added.")


    # --- Initialize and Add Utility Plugins to the Kernel ---
    print("🛠️ Initializing and adding utility plugins...")
    kernel.add_plugin(LocalRuleLoaderPlugin(), plugin_name="LocalRules")
    kernel.add_plugin(DocumentParsingPlugin(AZURE_DOC_INTEL_ENDPOINT, AZURE_DOC_INTEL_API_KEY), plugin_name="DocParser")
    # Image comprehension specifically uses the complex LLM for vision capabilities
    kernel.add_plugin(ImageComprehensionPlugin(kernel, complex_llm_service_id), plugin_name="ImageIntel") 
    print("✅ Utility plugins added.")

    # --- Initialize Agents (now inheriting from sk.agent.Agent) ---
    print("🤖 Initializing specialized agents with appropriate LLM services...")
    # Document processing for summarization can use the faster LLM
    doc_processing_agent = DocumentProcessingAgent(kernel, fast_llm_service_id)
    # Validation, security, and lead review require more complex reasoning, use the complex LLM
    structure_validator_agent = StructureValidatorAgent(kernel, complex_llm_service_id)
    security_architect_agent = SecurityArchitectAgent(kernel, complex_llm_service_id)
    lead_reviewer_agent = LeadReviewerAgent(kernel, complex_llm_service_id)
    print("✅ Agents initialized.")

    # --- Register Agent's Capabilities as Plugins for the Planner ---
    print("🔗 Registering agent capabilities as plugins for the planner...")
    kernel.add_plugin(doc_processing_agent, plugin_name="DocumentProcessor")
    kernel.add_plugin(structure_validator_agent, plugin_name="StructureValidator")
    kernel.add_plugin(security_architect_agent, plugin_name="SecurityArchitect")
    kernel.add_plugin(lead_reviewer_agent, plugin_name="LeadReviewer")
    print("✅ Agent capabilities registered as plugins.")


    # --- Define the Document to Review ---
    document_to_review = "test_data/arb.pdf" # Ensure this file exists for testing

    if not os.path.exists(document_to_review):
        print(f"Error: Sample document not found at {document_to_review}. Please create it.")
        print("This example requires a PDF document at 'test_data/arb.pdf' for parsing.")
        return

    # --- Orchestration Goal for the Planner ---
    goal = (
        f"Analyze the architecture design document located at '{document_to_review}'. "
        "First, use the DocumentProcessor to extract and summarize its content into a comprehensive design summary. "
        "Then, use the StructureValidator to validate the summary against structural rules and determine if any critical errors exist. "
        "If critical structural errors are found, stop further detailed reviews and consolidate only the structural report using the LeadReviewer. "
        "If no critical structural errors, then use the SecurityArchitect to concurrently review the document's security aspects. "
        "Finally, use the LeadReviewer to consolidate all review reports (structural and security) into a comprehensive final architecture review document. "
        "Present the final document."
    )

    print(f"\n🎯 Orchestration Goal: {goal}")

    # --- Initialize the Planner ---
    planner = SequentialPlanner(kernel=kernel, service_id=complex_llm_service_id) # Planner uses the complex LLM for reasoning

    # --- Create the Plan ---
    print("\n📝 Creating the execution plan...")
    plan = await planner.create_plan(goal)
    print("Generated Plan:\n")
    print(plan.as_xml())
    print("-" * 50)

    # --- Execute the Plan ---
    print("\n[Orchestrator] Executing steps based on the plan's logical flow...")

    # Step 1: Process Document (always first)
    print("\n[Orchestrator] Invoking DocumentProcessor to summarize the document...")
    comprehensive_summary = await doc_processing_agent.process_document(document_to_review)
    print("✅ Document processing and summary complete.")
    print(f"Comprehensive Summary (first 500 chars):\n{comprehensive_summary[:500]}...\n")


    # Step 2: Structural Validation
    print("\n[Orchestrator] Invoking StructureValidator to perform structural validation...")
    structure_validation_result_json_str = await structure_validator_agent.validate_document_structure(comprehensive_summary)
    structure_validation_data = json.loads(structure_validation_result_json_str)
    structural_report_text = structure_validation_data.get("report_text", "No structural report text.")
    has_critical_errors = structure_validation_data.get("has_critical_errors", False)
    print("✅ Structural validation complete.")
    print(structural_report_text)

    # --- Handoff Pattern ---
    if has_critical_errors:
        print("\n[Orchestrator] 🚨 CRITICAL STRUCTURAL ERRORS DETECTED. Halting further detailed reviews (Handoff Pattern).")
        final_report_summary = f"Architecture review halted due to critical structural errors:\n{structure_validation_data.get('critical_error_reason', 'Reason not specified.')}"
        final_report = await lead_reviewer_agent.consolidate_all_reports(
            structural_report=structural_report_text,
            other_reports_summary="No further detailed reviews performed due to critical structural errors. " + final_report_summary
        )
    else:
        print("\n[Orchestrator] 👍 No critical structural errors. Proceeding with detailed reviews (Concurrent Pattern).")
        
        # --- Concurrent Execution ---
        print("[Orchestrator] Initiating concurrent security review...")
        
        # We launch the security review concurrently
        security_task = security_architect_agent.review_document_security(comprehensive_summary)
        
        # You can add more concurrent tasks here if you had other detailed review agents:
        # infra_task = infra_architect_agent.review_document_infrastructure(comprehensive_summary)
        
        results = await asyncio.gather(security_task) # Add other tasks here: security_task, infra_task
        security_report = results[0] # Assuming security_task is the first in results
        
        print("✅ Concurrent detailed reviews completed.")
        print(f"Security Review Report (first 500 chars):\n{security_report[:500]}...\n")

        # --- Consolidation ---
        print("\n[Orchestrator] Consolidating all reports into the final document...")
        final_report = await lead_reviewer_agent.consolidate_all_reports(
            structural_report=structural_report_text,
            other_reports_summary=f"Security Review Report:\n{security_report}"
        )

    print("\n--- Final Architecture Review Document ---")
    print(final_report)
    print("\n--- Orchestration Complete ---")

if __name__ == "__main__":
    asyncio.run(main())