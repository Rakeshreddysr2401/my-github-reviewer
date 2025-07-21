# llm_config.py
import os
from langchain.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from utils.logger import get_logger
from dotenv import load_dotenv
load_dotenv()
log = get_logger()

# Registry of all supported providers and models
PROVIDER_REGISTRY = {
    "openai": {
        "gpt-4o": lambda temperature: ChatOpenAI(model="gpt-4o", temperature=temperature),
        "gpt-4o-mini": lambda temperature: ChatOpenAI(model="gpt-4o-mini", temperature=temperature),
        "gpt-4-turbo": lambda temperature: ChatOpenAI(model="gpt-4-turbo", temperature=temperature),
    },
    "ollama": {
        "llama3": lambda temperature: ChatOllama(model="llama3", temperature=temperature),
        "mistral": lambda temperature: ChatOllama(model="mistral", temperature=temperature),
        "phi3:mini": lambda temperature: ChatOllama(model="phi3:mini", temperature=temperature),
    },
    "gemini": {
        "gemini-pro": lambda temperature: ChatGoogleGenerativeAI(model="gemini-pro", temperature=temperature),
    },
    "anthropic": {
        "claude-3-opus": lambda temperature: ChatAnthropic(model="claude-3-opus-20240229", temperature=temperature),
        "claude-3-sonnet": lambda temperature: ChatAnthropic(model="claude-3-sonnet-20240229", temperature=temperature),
    },
}


def get_llm(provider: str = "openai", model: str = "gpt-4o-mini", temperature: float = 0.7):
    """Returns an LLM instance based on provider, model, and temperature."""
    provider = provider.lower()
    model = model.lower()

    log.info(f"LLM requested -> Provider: '{provider}', Model: '{model}', Temperature: {temperature}")

    provider_models = PROVIDER_REGISTRY.get(provider)
    if not provider_models:
        supported = ", ".join(PROVIDER_REGISTRY.keys())
        log.error(f"Unsupported provider '{provider}'. Supported providers: {supported}")
        raise ValueError(f"Unsupported provider '{provider}'. Supported providers: {supported}")

    model_loader = provider_models.get(model)
    if not model_loader:
        supported = ", ".join(provider_models.keys())
        log.error(f"Unsupported model '{model}' for provider '{provider}'. Supported models: {supported}")
        raise ValueError(f"Unsupported model '{model}' for provider '{provider}'. Supported models: {supported}")

    log.info(f"Loading model '{model}' from provider '{provider}' with temperature={temperature}")
    return model_loader(temperature)
