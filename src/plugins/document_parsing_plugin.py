# src/plugins/local_rule_loader_plugin.py
import os
import yaml
from semantic_kernel import kernel_function

class LocalRuleLoaderPlugin:
    def __init__(self, rules_dir: str = "rules"):
        self._rules_dir = rules_dir

    @kernel_function(
        description="Loads a set of rules from a local YAML file.",
        name="LoadRules",
        input_description="The name of the YAML file (e.g., 'structural_rules.yaml') containing the rules."
    )
    async def load_rules(self, rule_file_name: str) -> str:
        """
        Loads rules from a specified YAML file in the 'rules' directory.
        """
        file_path = os.path.join(self._rules_dir, rule_file_name)
        if not os.path.exists(file_path):
            return f"Error: Rule file '{rule_file_name}' not found at {file_path}"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            # Convert list of dicts to a readable string for the LLM
            return "\n".join([f"- {rule.get('id')}: {rule.get('description')} (Critical: {rule.get('critical')})" for rule in rules])
        except Exception as e:
            return f"Error loading rules from {rule_file_name}: {e}"