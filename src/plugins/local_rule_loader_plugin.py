import semantic_kernel as sk
from semantic_kernel.functions import kernel_function

class LocalRuleLoaderPlugin:
    """
    A Semantic Kernel plugin to load rules from local text files.
    """
    @kernel_function(
        name="load_structure_rules",
        description="Loads structural validation rules from a local text file.",
        input_description="The file path to the text file containing the rules."
    )
    def load_structure_rules(self, file_path: str) -> str:
        """
        Loads rules from a specified local text file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = f.read()
            print(f"DEBUG: Successfully loaded rules from {file_path}")
            return rules
        except FileNotFoundError:
            print(f"ERROR: Rules file not found at {file_path}")
            return "Error: Rules file not found."
        except Exception as e:
            print(f"ERROR: Failed to load rules from {file_path}: {e}")
            return f"Error loading rules: {str(e)}"