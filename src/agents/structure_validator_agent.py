# src/agents/structure_validator_agent.py
import json
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import PromptTemplate, PromptTemplateConfig

class StructureValidatorAgent(Agent):
    def __init__(self, kernel: sk.Kernel, service_id: str = "default"):
        super().__init__(
            kernel=kernel,
            service_id=service_id,
            name="StructureValidator",
            description="Agent for validating the structural integrity of a design document against rules.",
            instructions=(
                "You are a meticulous architectural document structural validator. "
                "Your task is to review a design proposal summary against a set of structural rules. "
                "For each rule, determine if it's met, violated, or not applicable. "
                "Identify if any *critical* rules are violated. "
                "Generate a detailed report in JSON format, indicating the rule evaluation and "
                "a boolean flag for 'has_critical_errors'. If critical errors are found, "
                "provide a concise reason. The JSON should be wrapped in ```json tags."
            )
        )
        self._local_rule_loader = kernel.plugins["LocalRules"]
        self._llm = kernel.get_service(service_id)

    @kernel_function(
        description="Validates a design document summary against structural rules.",
        name="ValidateDocumentStructure",
        input_description="The comprehensive summary of the design document."
    )
    async def validate_document_structure(self, comprehensive_summary: str) -> str:
        print("[StructureValidator] Starting structural validation...")
        
        # Load structural rules - UPDATED FILE NAME HERE
        structural_rules = await self._local_rule_loader.invoke("LoadRules", sk.KernelArguments(rule_file_name="structural_rules.yaml"))
        print(f"[StructureValidator] Loaded structural rules: \n{structural_rules[:200]}...") # Print first 200 chars

        prompt_template = PromptTemplate(
            template=(
                "As an architectural document structural validator, analyze the following design proposal summary "
                "against the provided **structural rules**. For each rule, state if it's 'Met', 'Violated', or 'Not Applicable'. " # UPDATED PROMPT LANGUAGE
                "If violated, provide a brief explanation. "
                "Finally, determine if any *critical* rules are violated. "
                "Output your findings as a JSON object with 'rule_evaluations' (list of rule ID, status, explanation), "
                "and 'has_critical_errors' (boolean). If 'has_critical_errors' is true, include a 'critical_error_reason' string.\n\n"
                "Design Proposal Summary:\n{{"
                "$"
                "input_summary}}\n\n"
                "Structural Rules:\n{{"
                "$"
                "input_rules}}\n\n"
                "JSON Report:"
            ),
            prompt_template_config=PromptTemplateConfig(
                input_variables=[
                    sk.semantickernel.input_variable.InputVariable(name="input_summary", description="The document summary."),
                    sk.semantickernel.input_variable.InputVariable(name="input_rules", description="The structural rules to evaluate against.")
                ],
                execution_settings=self._llm.get_prompt_execution_settings(service_id=self.service_id, max_tokens=1500, temperature=0.0)
            )
        )
        
        validation_function = self._llm.get_chat_message_content(
            messages=sk.contents.chat_history.ChatHistory().add_user_message(f"Input Summary:\n{comprehensive_summary}\n\nRules:\n{structural_rules}"),
            prompt_template=prompt_template,
            kernel=self._kernel
        )

        raw_response = await validation_function
        report_str = raw_response.content.strip()

        # Extract JSON from markdown if present
        if report_str.startswith("```json") and report_str.endswith("```"):
            report_str = report_str[len("```json"): -len("```")].strip()

        try:
            validation_data = json.loads(report_str)
            print("[StructureValidator] Structural validation completed.")
            
            # Add a 'report_text' field for the consolidated report
            validation_data['report_text'] = f"Structural Validation Report:\n"
            for eval in validation_data.get('rule_evaluations', []):
                validation_data['report_text'] += f"- Rule {eval.get('id')}: {eval.get('status')}"
                if eval.get('explanation'):
                    validation_data['report_text'] += f" - {eval.get('explanation')}"
                validation_data['report_text'] += "\n"
            
            if validation_data.get('has_critical_errors'):
                validation_data['report_text'] += f"\nCRITICAL ERRORS DETECTED: {validation_data.get('critical_error_reason', 'Reason not provided.')}\n"
            else:
                validation_data['report_text'] += "\nNo critical structural errors detected.\n"

            return json.dumps(validation_data)

        except json.JSONDecodeError as e:
            print(f"[StructureValidator] JSON parsing error: {e}")
            print(f"Raw response: {report_str}")
            return json.dumps({
                "rule_evaluations": [],
                "has_critical_errors": True, # Assume critical error if JSON is malformed
                "critical_error_reason": f"Validation agent produced malformed JSON output: {e}. Raw output: {report_str[:200]}...",
                "report_text": f"Structural Validation Failed: Malformed response from agent. {e}. Raw output: {report_str[:200]}..."
            })
        except Exception as e:
            print(f"[StructureValidator] Unexpected error during validation: {e}")
            return json.dumps({
                "rule_evaluations": [],
                "has_critical_errors": True,
                "critical_error_reason": f"Unexpected error during validation: {e}",
                "report_text": f"Structural Validation Failed: Unexpected error. {e}"
            })