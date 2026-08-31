"""Versioned prompt templates for evidence-grounded explanations."""

PROMPT_VERSION = "phase5-v1"
SYSTEM_PROMPT = "Use only validated tool results. Never invent routes, costs, probabilities, or feasibility. If evidence is missing, state that clearly."
TEMPLATES = {
    "decision_explanation": "Explain the selected decision using the evidence, alternatives, and uncertainty fields.",
    "counterfactual": "Compare baseline and isolated scenario results using only structured metrics.",
    "experiment_summary": "Summarize the experiment and state the measured winner without adding unsupported claims.",
}
