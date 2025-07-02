````markdown
# 🏛️ Architecture Review Orchestrator

This project demonstrates an intelligent architecture review system built using **Semantic Kernel (SK)**, leveraging its latest `Agent` framework, `SequentialPlanner`, and various plugins to automate the process of analyzing design documents, validating their structure, assessing security, and consolidating findings into a comprehensive report.

## 🌟 Project Overview

The Architecture Review Orchestrator aims to streamline the often complex and multi-faceted task of reviewing technical design documents. It simulates a team of specialized AI agents working collaboratively under an orchestration layer to perform distinct review functions.

**Key Capabilities:**

* **Document Processing:** Extracts and summarizes content from design documents (e.g., PDFs).

* **Structural Validation:** Checks the document's adherence to predefined architectural structural rules.

* **Conditional Handoff:** Halts further detailed reviews if critical structural errors are detected, ensuring early feedback.

* **Concurrent Detailed Reviews:** If structural validation passes, it initiates parallel security reviews.

* **Report Consolidation:** Synthesizes findings from all review stages into a single, cohesive final report.

* **Dynamic LLM Selection:** Utilizes different Large Language Models (LLMs) optimized for specific tasks (e.g., faster/cheaper models for summarization, more powerful/multimodal models for complex reasoning and vision).

## 💡 Design Philosophy

This prototype adopts a **hybrid orchestration model** to balance the intelligence of AI planners with the need for deterministic control in critical business workflows:

* **Semantic Kernel's `SequentialPlanner` for High-Level Reasoning:** The `SequentialPlanner` is used to interpret a natural language goal and propose a logical sequence of high-level steps (i.e., which agents/capabilities are needed and in what order). This leverages the LLM's ability to understand intent and map it to available tools.

* **Programmatic Control for Deterministic Logic:** For complex conditional branching (like the "handoff" if critical errors are found) and explicit concurrent execution (for detailed reviews), the `main.py` script takes over. This ensures reliability, predictability, and easier debugging for crucial workflow decisions that current AI planners might not yet handle deterministically within their generated plans.

* **First-Class `sk.agent.Agent` Components:** Specialized review functions are encapsulated within custom Python classes that inherit from `semantic_kernel.agent.Agent`. This provides clear role definitions, enhances modularity, and aligns with the latest Semantic Kernel best practices for building autonomous agents.

* **Reusable Plugins (Tools):** Common functionalities (like document parsing, image comprehension, rule loading) are implemented as standard Semantic Kernel plugins, making them discoverable and usable by any agent or function within the system via the central `Kernel`.

## 🔄 Component Interaction Diagram

```mermaid
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
````

## 📦 Project Structure

```
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
```

## 🛠️ Installation Instructions

### Prerequisites

  * **Python 3.9+**

  * **Azure Subscription:**

      * **Azure OpenAI Service:** Deploy at least two models:

          * One for **complex reasoning and multimodal tasks** (e.g., `gpt-4o` or `gpt-4`). Note its deployment name.

          * One for **fast, text-only summarization** (e.g., `gpt-35-turbo`). Note its deployment name.

      * **Azure AI Document Intelligence:** Create a Document Intelligence resource. Note its endpoint and API key.

### Steps

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    (If `requirements.txt` is not provided, manually install the following):

    ```bash
    pip install semantic-kernel python-dotenv pyyaml azure-ai-formrecognizer
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` in the root directory of your project and populate it with your Azure credentials. Remember to put all values in quotes.

    ```dotenv
    # .env
    AZURE_OPENAI_ENDPOINT="[https://your-openai-resource.openai.azure.com/](https://your-openai-resource.openai.azure.com/)"
    AZURE_OPENAI_API_KEY="your_azure_openai_api_key_here"
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" # Or use another stable version like "2023-05-15"

    # Deployment for complex tasks and vision
    AZURE_DEPLOYMENT_NAME_COMPLEX="your-gpt4o-deployment"
    AZURE_MODEL_ID_COMPLEX="gpt-4o" # e.g., gpt-4o, gpt-4-vision-preview, gpt-4

    # Deployment for fast/cheap text-only tasks
    AZURE_DEPLOYMENT_NAME_FAST="your-gpt35-turbo-deployment"
    AZURE_MODEL_ID_FAST="gpt-35-turbo" # e.g., gpt-35-turbo, gpt-35-turbo-16k

    AZURE_DOC_INTEL_ENDPOINT="[https://your-doc-intel-resource.cognitiveservices.azure.com/](https://your-doc-intel-resource.cognitiveservices.azure.com/)"
    AZURE_DOC_INTEL_API_KEY="your_azure_doc_intel_api_key_here"
    ```

    Replace the placeholder values with your actual Azure service details.

5.  **Prepare Sample Data:**
    Create a directory named `test_data/` in the root of your project.
    Place a sample PDF architecture design document (e.g., `architecture_design.pdf`) inside this `test_data/` directory.
    Ensure the `main.py` script's `document_to_review` variable points to this file (e.g., `document_to_review = "test_data/architecture_design.pdf"`).

6.  **Create Structural Rules File:**
    Ensure the `rules/structural_rules.yaml` file exists with the following content:

    ```yaml
    # rules/structural_rules.yaml
    - id: SR-001
      description: "Must contain an 'Architecture Diagram' or 'System Overview Diagram'."
      critical: true
    - id: SR-002
      description: "Must contain a 'Business Context' or 'Problem Statement' section."
      critical: true
    - id: SR-003
      description: "Must contain a 'Data Flow Diagram' or 'Data Model' description."
      critical: true
    - id: SR-004
      description: "Must clearly define 'Security Considerations' or 'Security Design'."
      critical: true
    ```

7.  **Run the Application:**

    ```bash
    python main.py
    ```

The orchestrator will then execute the review process, printing progress and the final architecture review document to the console.

## 🚀 Future Enhancements & Considerations

  * **More Robust Error Handling:** Implement more granular error handling and retry mechanisms for external API calls and LLM interactions.

  * **User Interface:** Develop a web-based UI (e.g., with Flask/FastAPI backend and React/Vue frontend) to provide a more interactive experience for uploading documents, viewing progress, and reviewing reports.

  * **Advanced Planner Integration:** As Semantic Kernel's planners evolve, explore deeper integration of complex conditional and concurrent logic directly within the planner's execution capabilities, potentially reducing the need for explicit programmatic control in `main.py`.

  * **Additional Review Agents:** Expand the system with more specialized agents (e.g., Cost Optimization Agent, Performance Review Agent, Data Governance Agent).

  * **Human-in-the-Loop:** Introduce mechanisms for human intervention and approval at critical stages of the review process.

  * **Memory and State Management:** Implement more sophisticated memory management for agents to retain context across multiple interactions or long-running processes.

  * **Output Formats:** Allow the final report to be generated in various formats (e.g., Markdown, HTML, DOCX).

<!-- end list -->

```
```