"""
Recommendation Agent
====================
Agent 4 of 5 in the Agentic AI Pipeline.

Generates actionable pharmaceutical manufacturing recommendations,
corrective actions, and suggested investigation areas based on the
decision and top SHAP feature contributors. Integrates with local Ollama
(llama3) to generate dynamic, context-aware CAPA plans.
"""
import httpx
import json

class RecommendationAgent:
    """Agent responsible for prescriptive guidance and corrective action plans (CAPA)."""

    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="llama3"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def recommend(self, decision: str, shap_values: dict = None) -> dict:
        """
        Generate recommendations, corrective actions, and investigation guidance.
        
        Args:
            decision: 'Approved', 'Rework', or 'Rejected'
            shap_values: Dict of {feature_name: shap_value}
            
        Returns:
            dict: {recommendation, corrective_action, investigation}
        """
        shap_values = shap_values or {}
        top_features = list(shap_values.keys())[:5] if shap_values else []
        
        # Fallback default recommendations
        default_recs = self._get_fallback_recommendations(decision, top_features)

        # Prompt for Ollama
        prompt = f"""You are a Senior Pharmaceutical Quality Assurance AI.
A batch of API tablets was just evaluated.
The decision for this batch is: {decision}.
The top 5 critical parameters that influenced this decision (based on SHAP values) are: {', '.join(top_features) if top_features else 'Unknown'}.

Based on this, generate a highly professional Corrective and Preventive Action (CAPA) plan.
You MUST format your response as a valid JSON object with EXACTLY these three keys:
1. "recommendation": A 1-2 sentence summary of the status and primary concern.
2. "corrective_action": 3 numbered steps for immediate correction.
3. "investigation": 3 numbered steps for root-cause investigation.

Do not output any markdown formatting, only raw JSON.
Example format:
{{
  "recommendation": "Batch meets criteria...",
  "corrective_action": "1. Step one...\\n2. Step two...",
  "investigation": "1. Investigate A...\\n2. Investigate B..."
}}
"""
        
        try:
            # Call Ollama API
            response = httpx.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=3.0
            )
            
            if response.status_code == 200:
                data = response.json()
                llm_text = data.get("response", "").strip()
                
                # Parse the JSON response
                try:
                    capa_json = json.loads(llm_text)
                    if all(k in capa_json for k in ["recommendation", "corrective_action", "investigation"]):
                        return capa_json
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"[Recommendation Agent] Ollama generation failed, using fallback: {e}")
            
        return default_recs

    def _get_fallback_recommendations(self, decision: str, top_features: list) -> dict:
        if decision == 'Approved':
            rec = ("Batch meets all predictive pharmaceutical quality specifications. "
                   "Recommended to proceed with final packaging and commercial release clearance.")
            ca = "None required. Standard in-line process monitoring should be maintained."
            inv = "No investigation required. All operational parameters remain within validated normal operating ranges."
        elif decision == 'Rework':
            feat_str = ", ".join(top_features) if top_features else "process parameters"
            rec = (f"Batch exhibits borderline quality parameters driven primarily by {feat_str}. "
                   "Recommended for secondary technical review and potential reprocessing/re-drying.")
            ca = ("1. Perform secondary drying cycle if moisture levels are elevated.\n"
                  "2. Re-evaluate compression force settings and tablet hardness uniformity.\n"
                  "3. Verify force-feeder speed and blend flowability prior to re-compression.")
            inv = ("1. Inspect main compression punches for wear or powder sticking.\n"
                   "2. Review Granulation moisture logs and drying temperature curves.\n"
                   "3. Audit operator parameter adjustments during the batch run.")
        else: # Rejected
            feat_str = ", ".join(top_features) if top_features else "critical parameters"
            rec = (f"Batch failed quality prediction criteria due to severe deviations in {feat_str}. "
                   "Recommended to PLACE BATCH ON HOLD and initiate Out-Of-Specification (OOS) investigation.")
            ca = ("1. Quarantine entire batch lot immediately in accordance with site SOPs.\n"
                  "2. Initiate formal Corrective and Preventive Action (CAPA) procedure.\n"
                  "3. Perform full analytical laboratory testing (Dissolution, HPLC Impurity Profile, Residual Solvents).")
            inv = ("1. Root-cause analysis of Raw Material API lot purity and particle size distribution.\n"
                   "2. Technical audit of compression machine sensors and force calibration records.\n"
                   "3. Review environmental humidity and temperature logs during processing.")

        return {
            'recommendation': rec,
            'corrective_action': ca,
            'investigation': inv
        }
