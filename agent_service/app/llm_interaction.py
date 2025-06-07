import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from app.logger import setup_logger

log = setup_logger()
load_dotenv()


class LLMInteraction:
    def __init__(self, system_prompt: str, model_name: str = "llama3:latest"):
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")  # Default URL
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.model = ChatOllama(
            base_url=self.base_url,
            model=self.model_name,
            temperature=self.temperature
        )

    def run(self, user_input: str) -> str:
        """Sends the user input and system prompt to the model."""
        log.info(f"[LLM Interaction] Sending request to Ollama model: {self.model_name} with input: {user_input}")

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]

        try:
            response = self.model.invoke(messages)
            log.info(f"[LLM Interaction] Response from Ollama: {response.content}")
            return response.content
        except Exception as e:
            log.error(f"[LLM Interaction] Error calling Ollama: {str(e)}")
            return f"Error: {str(e)}"
