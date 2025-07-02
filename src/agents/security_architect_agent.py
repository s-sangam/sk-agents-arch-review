# src/agents/security_architect_agent.py
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import PromptTemplate, PromptTemplateConfig

class SecurityArchitectAgent(Agent):
    def __init__(self, kernel: sk.Kernel, service_id: str = "default"):
        super().__init__(
            kernel=kernel,
            service_id=service_id,
            name="SecurityArchitect",
            description="Agent specialized in reviewing document security and compliance.",
            instructions=(
                "You are a highly skilled cybersecurity architect. Your role is to critically "
                "evaluate the provided design proposal summary from a security and compliance perspective. "
                "Identify potential vulnerabilities, recommend best practices, and assess adherence "
                "to common security principles (e.g., least privilege, defense-in-depth, data encryption). "
                "Generate a concise security review report."
            )
        )
        self._llm = kernel.get_service(service_id)

    @kernel_function(
        description="Reviews a design document summary for security vulnerabilities and compliance.",
        name="ReviewDocumentSecurity",
        input_description="The comprehensive summary of the design document."
    )
    async def review_document_security(self, comprehensive_summary: str) -> str:
        print("[SecurityArchitect] Starting security review...")

        prompt_template = PromptTemplate(
            template=(
                "As a cybersecurity architect, conduct a thorough security review of the following "
                "design proposal summary. Focus on identifying potential vulnerabilities, "
                "compliance concerns, and areas where security best practices could be applied or improved. "
                "Provide actionable recommendations.\n\n"
                "Design Proposal Summary:\n{{"
                "$"
                "input}}\n\n"
                "Security Review Report (Concise and Actionable):"
            ),
            prompt_template_config=PromptTemplateConfig(
                input_variables=[sk.semantickernel.input_variable.InputVariable(name="input", description="The document summary for security review.")],
                execution_settings=self._llm.get_prompt_execution_settings(service_id=self.service_id, max_tokens=700, temperature=0.3)
            )
        )
        
        security_review_function = self._llm.get_chat_message_content(
            messages=comprehensive_summary,
            prompt_template=prompt_template,
            kernel=self._kernel
        )

        security_report = await security_review_function
        print("[SecurityArchitect] Security review completed.")
        return security_report.content