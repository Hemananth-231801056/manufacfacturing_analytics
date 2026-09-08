"""
Decision Agent
================
Agent 3 of 5 in the Agentic AI Pipeline.

Evaluates prediction outcome along with model confidence scores to assign
the final release status: Approved, Rework, or Rejected.
Applies confidence thresholds to flag borderline or low-confidence cases.
"""

class DecisionAgent:
    """Agent responsible for final release status and confidence evaluation."""

    def decide(self, prediction: str, confidence: float, confidence_scores: dict) -> dict:
        """
        Evaluate prediction and confidence score to determine final decision.
        
        Confidence Logic:
        - Confidence >= 80%: High Confidence decision.
        - 60% <= Confidence < 80%: Medium Confidence decision — QA Review Recommended.
        - Confidence < 60%: Low Confidence decision — Manual Assessment Required.
        
        Args:
            prediction: Predicted class ('Approved', 'Rework', 'Rejected')
            confidence: Max probability score (0.0 to 1.0)
            confidence_scores: Dict of probabilities per class
            
        Returns:
            dict: {decision, decision_details, review_required}
        """
        conf_pct = confidence * 100.0

        if confidence >= 0.80:
            conf_level = "High"
            review_required = False
            details = (f"High confidence ({conf_pct:.1f}%) prediction for status '{prediction}'. "
                       f"Model parameters indicate strong alignment with historical {prediction} batch profiles.")
        elif confidence >= 0.60:
            conf_level = "Medium"
            review_required = True
            details = (f"Medium confidence ({conf_pct:.1f}%) prediction for status '{prediction}'. "
                       f"Borderline parameter distribution detected. Quality Assurance review is recommended.")
        else:
            conf_level = "Low"
            review_required = True
            details = (f"Low confidence ({conf_pct:.1f}%) prediction for status '{prediction}'. "
                       f"High parameter uncertainty detected. Manual laboratory assessment and QA audit required.")

        return {
            'decision': prediction,
            'confidence_level': conf_level,
            'decision_details': details,
            'review_required': review_required
        }
