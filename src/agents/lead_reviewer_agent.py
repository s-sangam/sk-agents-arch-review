# src/agents/lead_reviewer_agent.py
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import PromptTemplate, PromptTemplateConfig

class LeadReviewerAgent(Agent):
    def __init__(self, kernel: sk.Kernel, service_id: str = "default"):
        super().__init__(
            kernel=kernel,
            service_id=service_id,
            name="LeadReviewer",
            description="Agent responsible for consolidating all review reports into a final document.",
            instructions=(
                "You are the Lead Architect Reviewer. Your final task is to consolidate various "
                "review reports (structural, security, etc.) into a single, cohesive, "
                "and professional Final Architecture Review Document. "
                "Synthesize findings, highlight key conclusions, and present actionable recommendations."
            )
        )
        self._llm = kernel.get_service(service_id)

    @kernel_function(
        description="Consolidates various review reports into a single, final architecture review document.",
        name="ConsolidateAllReports",
        input_description="A JSON string containing 'structural_report' and 'other_reports_summary'. "
                          "If 'other_reports_summary' is empty, indicate that no further reviews were performed."
    )
    async def consolidate_all_reports(self, structural_report: str, other_reports_summary: str = "") -> str:
        print("[LeadReviewer] Starting final report consolidation...")

        report_details = f"Structural Review:\n{structural_report}\n\n"
        if other_reports_summary:
            report_details += f"Detailed Reviews Summary:\n{other_reports_summary}\n"
        else:
            report_details += "Detailed reviews were not performed or results were not available.\n"

        prompt_template = PromptTemplate(
            template=(
                "As the Lead Architect Reviewer, synthesize the following review findings into a "
                "single, professional, and comprehensive Final Architecture Review Document. "
                "Provide an Executive Summary, detailed findings from each review section, "
                "and clear, actionable recommendations.\n\n"
                "Review Findings:\n{{"
                "$"
                "input}}\n\n"
                "Final Architecture Review Document:"
            ),
            prompt_template_config=PromptTemplateConfig(
                input_variables=[sk.semantickernel.input_variable.InputVariable(name="input", description="The combined review reports.")],
                execution_settings=self._llm.get_prompt_execution_settings(service_id=self.service_id, max_tokens=1500, temperature=0.2)
            )
        )

        consolidation_function = self._llm.get_chat_message_content(
            messages=report_details,
            prompt_template=prompt_template,
            kernel=self._kernel
        )

        final_report = await consolidation_function
        print("[LeadReviewer] Final report consolidation completed.")
        return final_report.content