# src/plugins/image_comprehension_plugin.py
import semantic_kernel as sk
from semantic_kernel import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.prompt_template import PromptTemplate

class ImageComprehensionPlugin:
    def __init__(self, kernel: sk.Kernel, chat_service_id: str):
        self._kernel = kernel
        self._chat_service_id = chat_service_id # Store the specific service ID
        self._chat_service = kernel.get_service(chat_service_id) # Get the service instance

    @kernel_function(
        description="Analyzes an image and provides a detailed description or answers questions about its content.",
        name="ComprehendImage",
        input_description="A base64 encoded string of the image, and a question about its content."
    )
    async def comprehend_image(self, image_base64: str, question: str) -> str:
        """
        Comprehends an image given its base64 encoded string and a question about it.
        """
        try:
            # Ensure the service is an AzureChatCompletion for vision capabilities
            if not isinstance(self._chat_service, AzureChatCompletion):
                raise TypeError("Chat service must be an AzureChatCompletion instance for image comprehension.")

            chat_history = ChatHistory()
            chat_history.add_user_message(
                [
                    ChatMessageContent(role=sk.AuthorRole.USER, content=question),
                    ChatMessageContent(role=sk.AuthorRole.USER, image_base64=image_base64)
                ]
            )

            # Use a basic prompt as the question itself is part of the message content
            prompt_config = PromptTemplateConfig("{{$input}}")
            prompt_template = PromptTemplate(prompt_config)
            
            # Use the specific chat service for vision
            vision_function = self._chat_service.get_chat_message_content(
                chat_history=chat_history,
                prompt_template=prompt_template,
                kernel=self._kernel # Pass the kernel
            )
            
            response = await vision_function
            return response.content

        except Exception as e:
            print(f"Error comprehending image: {e}")
            return f"Error: Could not comprehend image due to {e}"