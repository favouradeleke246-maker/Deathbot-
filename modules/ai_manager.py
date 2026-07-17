import json
import requests
import groq
import google.generativeai as genai
from config import GROQ_API_KEY, GOOGLE_API_KEY, OLLAMA_URL, DEFAULT_AI, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from openai import OpenAI
from modules.utils import logger

class AIManager:
    def __init__(self):
        self.providers = {}
        self.active_provider = None

        # Groq
        if GROQ_API_KEY:
            self.providers['groq'] = {
                'client': groq.Client(api_key=GROQ_API_KEY),
                'models': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']
            }

        # Gemini
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.providers['gemini'] = {
                'model': genai.GenerativeModel('gemini-2.5-flash'),
                'models': ['gemini-2.5-flash', 'gemini-3.1-flash-lite']
            }

        # DeepSeek (new)
        if DEEPSEEK_API_KEY:
            self.providers['deepseek'] = {
                'client': OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL or 'https://api.deepseek.com'),
                'models': ['deepseek-v4-pro', 'deepseek-v4-flash']
            }

        # Ollama
        if OLLAMA_URL:
            self.providers['ollama'] = {
                'url': OLLAMA_URL,
                'models': ['llama3', 'mistral', 'phi']
            }

        self.set_active_provider(DEFAULT_AI or 'groq')

    def set_active_provider(self, name):
        if name in self.providers:
            self.active_provider = name
            logger.info(f"AI provider set to: {name}")
        else:
            logger.warning(f"Provider {name} not available. Using groq.")
            self.active_provider = 'groq' if 'groq' in self.providers else list(self.providers.keys())[0]

    def _call_provider(self, provider, model, prompt, max_tokens=400, temperature=0.2):
        if provider == 'groq':
            client = self.providers['groq']['client']
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        elif provider == 'gemini':
            model_obj = self.providers['gemini']['model']
            response = model_obj.generate_content(prompt)
            return response.text

        elif provider == 'deepseek':
            client = self.providers['deepseek']['client']
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        elif provider == 'ollama':
            url = self.providers['ollama']['url'] + '/api/generate'
            payload = {"model": model, "prompt": prompt, "stream": False}
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json().get('response', '')
            else:
                raise Exception(f"Ollama error: {resp.status_code}")

        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate(self, prompt, max_tokens=400, temperature=0.2, provider=None, model=None):
        if provider is None:
            provider = self.active_provider
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not registered.")

        provider_data = self.providers[provider]
        if model is None:
            model = provider_data['models'][0]

        try:
            return self._call_provider(provider, model, prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"{provider} failed: {e}")
            for fallback_provider in self.providers:
                if fallback_provider != provider:
                    try:
                        logger.info(f"Falling back to {fallback_provider}")
                        return self._call_provider(fallback_provider, self.providers[fallback_provider]['models'][0], prompt, max_tokens, temperature)
                    except:
                        continue
            raise RuntimeError("All AI providers failed.")
