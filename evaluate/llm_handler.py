import os

from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_together import ChatTogether
from langchain_openai import ChatOpenAI
from langchain_fireworks import ChatFireworks
from langchain_ollama import ChatOllama


class LLMHandler:
    """
    A class to handle different LLM providers (Mistral, Anthropic, and Google) using LangChain integrations.
    """

    def __init__(self):
        self.available_models = {
            "ollama": [
                "llama3.2:3b",
                "mistral:7b"
            ],
            # "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            # "mistral": [
            #     "open-mistral-nemo-2407",
            #     "ministral-8b-2410",
            #     "mistral-small-2409",
            #     "mistral-large-2411",
            #     "mistral-small-2501",
            # ],
            # "google": [
            #     "gemini-2.0-flash-exp",
            #     "gemini-1.5-flash",
            #     "gemini-1.5-pro",
            #     "gemini-2.0-flash-001",
            # ],
            # "together": [
            #     "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            #     "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            #     "deepseek-ai/DeepSeek-R1",
            #     "deepseek-ai/DeepSeek-V3",
            # ],
            # "openai": [
            #     "gpt-4o-2024-11-20",
            #     "gpt-4o-mini",
            #     "o1-2024-12-17",
            #     "o3-mini-2025-01-31",
            # ],
            # "fireworks": [
            #     "accounts/fireworks/models/qwen-qwq-32b-preview",
            #     "accounts/fireworks/models/qwen2p5-72b-instruct",
            #     "accounts/fireworks/models/deepseek-v3",
            #     "accounts/fireworks/models/deepseek-r1",
            # ],
        }
        self.model_types = {
            "llama3.2:3b": "open-source",
            "mistral:7b": "open-source",
            "claude-3-5-sonnet-20241022": "private",
            "claude-3-5-haiku-20241022": "private",
            "open-mistral-nemo-2407": "open-source",
            "ministral-8b-2410": "private",
            "mistral-small-2409": "private",
            "mistral-large-2411": "private",
            "gemini-2.0-flash-exp": "private",
            "gemini-1.5-flash": "private",
            "gemini-1.5-pro": "private",
            "gemini-2.0-flash-001": "private",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo": "open-source",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": "open-source",
            "gpt-4o-2024-11-20": "private",
            "gpt-4o-mini": "private",
            "o1-2024-12-17": "private",
            "accounts/fireworks/models/qwen-qwq-32b-preview": "open-source",
            "accounts/fireworks/models/qwen2p5-72b-instruct": "open-source",
            "accounts/fireworks/models/deepseek-v3": "open-source",
            "accounts/fireworks/models/deepseek-r1": "open-source",
        }

        # Model name patterns for auto-detection of client
        self.model_patterns = {
            "o1": "openai",
            "o3": "openai",
            "gpt-4o": "openai",
            "claude": "anthropic",
            "mistral-": "mistral",
            "ministral": "mistral",
            "gemini": "google",
            "mixtral": "together",
            "llama": "ollama",
            "fireworks": "fireworks",
            "r1": "together",
            "deepseek-v3": "together",
        }

    def _detect_provider(self, model_name: str) -> str:
        """
        Automatically detects the provider based on the model name.
        """
        for pattern, provider in self.model_patterns.items():
            if pattern in model_name.lower():
                return provider
        raise ValueError(f"Could not detect provider for model name: {model_name}")

    def _validate_model(self, provider: str, model_name: str) -> bool:
        """
        Validates if the requested model is available for the given provider.
        """
        if provider not in self.available_models:
            raise ValueError(
                f"Provider {provider} not supported. Available providers: {list(self.available_models.keys())}"
            )

        if model_name not in self.available_models[provider]:
            raise ValueError(
                f"Model {model_name} not available for {provider}. Available models: {self.available_models[provider]}"
            )

        return True

    def get_all_models(self):
        """
        Returns all available models from each provider as a list
        """
        all_models = []
        for provider, models in self.available_models.items():
            all_models.extend(models)
        return all_models

    def get_llm(
        self,
        model_name: str,
        provider: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> BaseChatModel:
        """
        Creates and returns an LLM instance based on the provider and model name.

        Args:
            provider: The LLM provider ("anthropic", "mistral", or "google")
            model_name: The specific model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            api_key: Optional API key (if not set in environment variables)
            **kwargs: Additional arguments to pass to the model constructor

        Returns:
            A LangChain chat model instance
        """
        # Auto-detect provider if not specified
        if provider is None:
            provider = self._detect_provider(model_name)

        self._validate_model(provider, model_name)

        # Set API key if provided
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key

        model_params = {"temperature": temperature, "max_tokens": max_tokens, **kwargs}

        # remove temperature if model name contains o1
        if ("o1" in model_name) or ("o3" in model_name):
            model_params.pop("temperature", None)

        # set temperature to 0.6 if model name contains r1
        if "r1" in model_name:
            model_params["temperature"] = 0.6

        # Remove None values
        model_params = {k: v for k, v in model_params.items() if v is not None}

        if provider == "anthropic":
            print("Using Anthropic AI")
            return ChatAnthropic(model_name=model_name, **model_params)

        elif provider == "mistral":
            print("Using Mistral AI")
            return ChatMistralAI(model_name=model_name, **model_params)

        elif provider == "google":
            print("Using Google Generative AI")
            return ChatGoogleGenerativeAI(model=model_name, **model_params)

        elif provider == "together":
            print("Using ChatTogether")
            return ChatTogether(model=model_name, **model_params)

        elif provider == "openai":
            print("Using OpenAI")
            return ChatOpenAI(model=model_name, **model_params)

        elif provider == "fireworks":
            print("Using Fireworks")
            return ChatFireworks(model=model_name, **model_params)
        
        elif provider == "ollama":
            print("Using Ollama")
            return ChatOllama(model="llama3.1:8b-instruct-q8_0", base_url="http://host.docker.internal:11434/v1",**model_params)
