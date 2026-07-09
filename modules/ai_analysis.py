import os
import json
import groq
import google.generativeai as genai
from config import GROQ_API_KEY, GOOGLE_API_KEY

class AIAnalyzer:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.groq_client = groq.Client(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        genai.configure(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro') if GOOGLE_API_KEY else None

    def analyze_target(self, target_data):
        prompt = f"Analyze this target profile for potential attack vectors: {json.dumps(target_data)}"
        raw = None  # ensure variable exists
        try:
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",  # updated model
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                raw = response.choices[0].message.content
            elif self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                raw = response.text
            else:
                raw = "No AI model configured."
        except Exception as e:
            raw = f"AI analysis failed: {str(e)}"
        return raw
