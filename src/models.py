from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_groq import groq
import os

load_dotenv()


@dataclass(frozen=True)
class Provider:
  name: str
  env_var: str
  is_cost: bool
  base_url: str | None
  model: str

PROVIDER = [
  Provider(
    name='openai/gpt-oss-120b',
    env_var='OPENAI_API_KEY',
    is_cost=True,
    base_url=None,
    model='gpt-oss-120b'
  ),
]

def select_provider() -> Provider:
  for provider in PROVIDER:
    if os.getenv(provider.env_var):
      return provider
    
  raise RuntimeError("No provider found. Please set the appropriate environment variable for a provider.")

def build_chat_model() -> tuple[groq, Provider]:
  provider= select_provider()
  kwargs= {
    "model": provider.model,
    "api_key": os.getenv(provider.env_var),
  }
  if provider.base_url is not None:
    kwargs["base_url"]= provider.base_url

  model= groq(**kwargs), provider 
