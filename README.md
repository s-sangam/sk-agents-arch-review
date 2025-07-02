🏛️ Architecture Review Orchestrator
This project demonstrates an intelligent architecture review system built using Semantic Kernel (SK), leveraging its latest Agent framework, SequentialPlanner, and various plugins to automate the process of analyzing design documents, validating their structure, assessing security, and consolidating findings into a comprehensive report.

🌟 Project Overview
The Architecture Review Orchestrator aims to streamline the often complex and multi-faceted task of reviewing technical design documents. It simulates a team of specialized AI agents working collaboratively under an orchestration layer to perform distinct review functions.

Key Capabilities:

Document Processing: Extracts and summarizes content from design documents (e.g., PDFs).

Structural Validation: Checks the document's adherence to predefined architectural structural rules.

Conditional Handoff: Halts further detailed reviews if critical structural errors are detected, ensuring early feedback.

Concurrent Detailed Reviews: If structural validation passes, it initiates parallel security reviews.

Report Consolidation: Synthesizes findings from all review stages into a single, cohesive final report.

Dynamic LLM Selection: Utilizes different Large Language Models (LLMs) optimized for specific tasks (e.g., faster/cheaper models for summarization, more powerful/multimodal models for complex reasoning and vision).

💡 Design Philosophy
This prototype adopts a hybrid orchestration model to balance the intelligence of AI planners with the need for deterministic control in critical business workflows:

Semantic Kernel's SequentialPlanner for High-Level Reasoning: The SequentialPlanner is used to interpret a natural language goal and propose a logical sequence of high-level steps (i.e., which agents/capabilities are needed and in what order). This leverages the LLM's ability to understand intent and map it to available tools.

Programmatic Control for Deterministic Logic: For complex conditional branching (like the "handoff" if critical errors are found) and explicit concurrent execution (for detailed reviews), the main.py script takes over. This ensures reliability, predictability, and easier debugging for crucial workflow decisions that current AI planners might not yet handle deterministically within their generated plans.

First-Class sk.agent.Agent Components: Specialized review functions are encapsulated within custom Python classes that inherit from semantic_kernel.agent.Agent. This provides clear role definitions, enhances modularity, and aligns with the latest Semantic Kernel best practices for building autonomous agents.

Reusable Plugins (Tools): Common functionalities (like document parsing, image comprehension, rule loading) are implemented as standard Semantic Kernel plugins, making them discoverable and usable by any agent or function within the system via the central Kernel.

🔄 Component Interaction Diagram
graph TD
    A[User Goal / Document] --> B(main.py Orchestrator)
    B --> C{Initialize Kernel & Services}
    C --> D[Register Utility Plugins]
    D --> E[Initialize SK Agents]
    E --> F[Register Agent Capabilities as Plugins for Planner]

    F --> G(SequentialPlanner)
    G -- "Analyzes Goal & Available Capabilities" --> H[Generated Plan (XML)]
    H --> I{main.py Interprets Plan & Executes}

    I -- "Step 1: Document Processing" --> J(DocumentProcessor Agent)
    J --> K[DocParser Plugin]
    J --> L[ImageIntel Plugin]
    K --> M[Azure Doc Intelligence]
    L --> N[Azure OpenAI Vision LLM]
    J -- "Comprehensive Summary" --> O[Output]

    O --> P(StructureValidator Agent)
    P --> Q[LocalRules Plugin]
    Q --> R[structural_rules.yaml]
    P -- "Structural Validation Report (JSON)" --> S{Check for Critical Errors?}

    S -- "YES (Handoff Pattern)" --> T[LeadReviewer Agent]
    S -- "NO (Concurrent Pattern)" --> U[SecurityArchitect Agent]
    U --> V[Azure OpenAI Complex LLM]
    U -- "Security Review Report" --> W[Output]

    T -- "Consolidate Structural Report" --> X(Final Architecture Review Document)
    W --> Y(Consolidate Reports)
    Y --> T
    T --> X

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:1px
    style D fill:#ddf,stroke:#333,stroke-width:1px
    style E fill:#eef,stroke:#333,stroke-width:1px
    style F fill:#f0f,stroke:#333,stroke-width:1px
    style G fill:#9cf,stroke:#333,stroke-width:2px
    style H fill:#fff,stroke:#333,stroke-dasharray: 5 5
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#cff,stroke:#333,stroke-width:2px
    style K fill:#ffc,stroke:#333,stroke-width:1px
    style L fill:#ffc,stroke:#333,stroke-width:1px
    style M fill:#eee,stroke:#333,stroke-width:1px
    style N fill:#eee,stroke:#333,stroke-width:1px
    style O fill:#fdf,stroke:#333,stroke-width:1px
    style P fill:#cff,stroke:#333,stroke-width:2px
    style Q fill:#ffc,stroke:#333,stroke-width:1px
    style R fill:#eee,stroke:#333,stroke-width:1px
    style S fill:#fcc,stroke:#333,stroke-width:2px
    style T fill:#cff,stroke:#333,stroke-width:2px
    style U fill:#cff,stroke:#333,stroke-width:2px
    style V fill:#eee,stroke:#333,stroke-width:1px
    style W fill:#fdf,stroke:#333,stroke-width:1px
    style X fill:#afa,stroke:#333,stroke-width:3px
    style Y fill:#fdf,stroke:#333,stroke-width:1px

Explanation of Flow:

User Goal / Document: The process begins with a user-defined goal (e.g., "Review this architecture document") and the document itself.

main.py Orchestrator: The central Python script that initializes the Semantic Kernel, configures services, and orchestrates the overall review process.

Initialize Kernel & Services: The Semantic Kernel instance is created, and various Azure OpenAI LLM services (e.g., complex_llm for GPT-4o, fast_llm for GPT-3.5-turbo) are registered.

Register Utility Plugins: Essential tools like DocumentParsingPlugin (for Azure Document Intelligence), ImageComprehensionPlugin (for Azure OpenAI Vision), and LocalRuleLoaderPlugin are added to the Kernel's global plugin collection.

Initialize SK Agents: Instances of our specialized sk.agent.Agent subclasses (DocumentProcessorAgent, StructureValidatorAgent, etc.) are created. Each agent is configured with the Kernel and a specific LLM service ID.

Register Agent Capabilities as Plugins for Planner: Crucially, the core methods of our sk.agent.Agent instances (e.g., DocumentProcessor.ProcessDocumentAndSummarize) are registered as KernelFunctions with the Kernel. This makes them discoverable by the SequentialPlanner.

SequentialPlanner: The planner receives the user's high-level goal and, using the registered agent capabilities, generates a conceptual plan (a linear sequence of steps).

Generated Plan (XML): The planner outputs an XML representation of its proposed sequence. This is printed for transparency but not directly executed for the entire workflow due to complex conditional/concurrent needs.

main.py Interprets Plan & Executes: The main.py script then programmatically executes the steps, adding explicit conditional (if/else) and concurrent (asyncio.gather) logic based on the outcomes of previous steps.

DocumentProcessor Agent: Invoked first to extract text and summarize the document. It uses DocParser (which calls Azure Document Intelligence) and ImageIntel (which calls Azure OpenAI Vision LLM). The summarization itself uses the fast_llm.

StructuralValidator Agent: Receives the comprehensive summary and validates it against structural_rules.yaml (loaded via LocalRules plugin). It uses the complex_llm for its reasoning.

Check for Critical Errors?: Based on the structural validation report, main.py makes a programmatic decision.

YES (Handoff Pattern): If critical errors are found, the process immediately "hands off" to the LeadReviewer Agent to consolidate only the structural report and halt further detailed reviews.

NO (Concurrent Pattern): If no critical errors, main.py initiates concurrent detailed reviews.

SecurityArchitect Agent: Runs concurrently (along with any other detailed review agents) to assess the document's security. It uses the complex_llm.

Consolidate Reports: Once all necessary reviews are complete, the LeadReviewer Agent consolidates all findings into the final architecture review document. It uses the complex_llm for synthesis.

Final Architecture Review Document: The ultimate output of the orchestration.

📦 Project Structure
.
├── .env                  # Environment variables for API keys
├── main.py               # Main orchestration script
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── document_processing_agent.py  # SK Agent for doc processing & summarization
│   │   ├── structure_validator_agent.py  # SK Agent for structural rule validation
│   │   ├── security_architect_agent.py   # SK Agent for security review
│   │   └── lead_reviewer_agent.py        # SK Agent for final report consolidation
│   └── plugins/
│       ├── __init__.py
│       ├── document_parsing_plugin.py    # Wrapper for Azure Document Intelligence
│       ├── image_comprehension_plugin.py # Wrapper for Azure OpenAI Vision
│       └── local_rule_loader_plugin.py   # Loads local YAML rule files
└── rules/
    └── structural_rules.yaml # Defines structural validation rules for architecture documents

🛠️ Installation Instructions
Prerequisites
Python 3.9+

Azure Subscription:

Azure OpenAI Service: Deploy at least two models:

One for complex reasoning and multimodal tasks (e.g., gpt-4o or gpt-4). Note its deployment name.

One for fast, text-only summarization (e.g., gpt-35-turbo). Note its deployment name.

Azure AI Document Intelligence: Create a Document Intelligence resource. Note its endpoint and API key.

Steps
Clone the Repository:

git clone <repository_url>
cd <repository_name>

Create a Virtual Environment (Recommended):

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

(If requirements.txt is not provided, manually install the following):

pip install semantic-kernel python-dotenv pyyaml azure-ai-formrecognizer

Configure Environment Variables:
Create a file named .env in the root directory of your project and populate it with your Azure credentials:

# .env
AZURE_OPENAI_ENDPOINT="YOUR_AZURE_OPENAI_ENDPOINT"
AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_API_KEY"

# Deployment for complex tasks and vision (e.g., gpt-4o or gpt-4)
AZURE_DEPLOYMENT_NAME_COMPLEX="YOUR_GPT_4O_OR_GPT_4_DEPLOYMENT_NAME" 
# Deployment for fast/cheap text-only tasks (e.g., gpt-35-turbo)
AZURE_DEPLOYMENT_NAME_FAST="YOUR_GPT_35_TURBO_DEPLOYMENT_NAME" 

AZURE_DOC_INTEL_ENDPOINT="YOUR_AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
AZURE_DOC_INTEL_API_KEY="YOUR_AZURE_DOCUMENT_INTELLIGENCE_API_KEY"

Replace the placeholder values with your actual Azure service details.

Prepare Sample Data:
Create a directory named test_data/ in the root of your project.
Place a sample PDF architecture design document (e.g., architecture_design.pdf) inside this test_data/ directory.
Ensure the main.py script's document_to_review variable points to this file (e.g., document_to_review = "test_data/architecture_design.pdf").

Create Structural Rules File:
Ensure the rules/structural_rules.yaml file exists with the content provided in the previous response.

Run the Application:

python main.py

The orchestrator will then execute the review process, printing progress and the final architecture review document to the console.

🚀 Future Enhancements & Considerations
More Robust Error Handling: Implement more granular error handling and retry mechanisms for external API calls and LLM interactions.

User Interface: Develop a web-based UI (e.g., with Flask/FastAPI backend and React/Vue frontend) to provide a more interactive experience for uploading documents, viewing progress, and reviewing reports.

Advanced Planner Integration: As Semantic Kernel's planners evolve, explore deeper integration of complex conditional and concurrent logic directly within the planner's execution capabilities, potentially reducing the need for explicit programmatic control in main.py.

Additional Review Agents: Expand the system with more specialized agents (e.g., Cost Optimization Agent, Performance Review Agent, Data Governance Agent).

Human-in-the-Loop: Introduce mechanisms for human intervention and approval at critical stages of the review process.

Memory and State Management: Implement more sophisticated memory management for agents to retain context across multiple interactions or long-running processes.

Output Formats: Allow the final report to be generated in various formats (e.g., Markdown, HTML, DOCX).