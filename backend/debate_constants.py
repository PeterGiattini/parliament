"""Common constants and configurations for the debate system.

This file serves as a single source of truth for shared debate elements.
"""

# LLM Configuration
LLM_CONFIG = {
    "model_name": "gemini-2.0-flash",
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "location": "us-central1",
}

# Debate Round Configuration
DEBATE_ROUNDS = {
    1: {
        "title": "Opening Statements",
        "type": "parallel",
        "description": "All agents provide their initial positions simultaneously",
    },
    2: {
        "title": "Rebuttal",
        "type": "sequential",
        "description": "Agents respond to each other's arguments in turn",
    },
    3: {
        "title": "Surrebuttal",
        "type": "sequential",
        "description": (
            "Agents defend their original position against rebuttal critiques"
        ),
    },
    4: {
        "title": "Synthesis",
        "type": "moderator",
        "description": "Neutral summary of the entire debate",
    },
}

# Common Agent Directives
AGENT_DIRECTIVES = {
    "stance_requirement": (
        "Your first sentence must state your position. You must then immediately "
        "present your single most compelling argument to support that position."
    ),
    "grounded_speculation": (
        "Grounded Speculation: To make your arguments concrete, you are permitted "
        "to introduce plausible, specific data points, scenarios, or outcomes. You "
        'must preface these with a phrase like "Assuming...", "If we project '
        'that...", "Let\'s assume for a moment that...", "If this policy were '
        'implemented, we might see...", "The potential consequences could '
        'include...", "This could lead to scenarios where...", "Assuming current '
        'technology trends...", "Based on typical implementation patterns...", or '
        "similar qualifying language."
    ),
    "persona_constraint": (
        "Constraint: Do not refer to your own role or persona (e.g., do not say "
        '"As an economist..." or "From an economic perspective..."). Argue from '
        "your perspective, don't describe it."
    ),
}

# Debate Prompts
DEBATE_PROMPTS = {
    "rebuttal": (
        "You have already provided your opening statement. Below are the opening "
        "statements from the other members of the panel.\n\n"
        "Your task is to now engage with their arguments.\n\n"
        "CRITICAL: You must argue consistently with the core position you took in "
        "Round 1. Your goal is to defend your initial stance while critiquing "
        "others. Do not fundamentally change your overall position "
        "(support/oppose).\n\n"
        "Critique: Directly address the points made by the other panelists that "
        "conflict with your principles or analysis. Identify specific flaws in "
        "their reasoning.\n\n"
        "Acknowledge & Reinforce: To make your arguments more credible, you may "
        "acknowledge valid points made by other panelists (even those you "
        "generally disagree with). Explain how their point actually reinforces "
        "your own position or helps clarify the true point of disagreement. For "
        "example: \"I agree with the Technologist's concern about logistical "
        "bottlenecks, which actually strengthens my argument that the economic "
        'costs are prohibitive."\n\n'
        "Refine: Briefly refine your own position based on this new information, "
        "but maintain your core stance.\n\n"
        "Your response should be a direct contribution to the ongoing debate, not "
        "a new opening statement. Be concise and targeted."
    ),
    "surrebuttal": (
        "You have now participated in both opening statements and rebuttal "
        "rounds. Below are the rebuttal responses from the other panelists, "
        "which may have critiqued your original position.\n\n"
        "Your task is to provide a final defense of your core position.\n\n"
        "CRITICAL: This is your last opportunity to defend your original stance. "
        "You must remain consistent with your Round 1 position while addressing "
        "the specific critiques leveled against you.\n\n"
        "Defend & Clarify: Address the specific criticisms of your arguments. "
        "Explain why your position remains valid despite these critiques. "
        "Clarify any misunderstandings of your original points.\n\n"
        "Strengthen: Reinforce your strongest arguments with additional "
        "reasoning or evidence. Show why your position is still the most "
        "compelling despite the counter-arguments.\n\n"
        "Conclude: End with a clear, confident restatement of your core "
        "position. This should be your final word on why your stance is "
        "correct.\n\n"
        "Your response should be a strong, final defense that leaves no doubt "
        "about where you stand. Be concise but thorough."
    ),
    "synthesis": (
        "You are a neutral, objective Moderator. You have been provided with the "
        "full transcript of a debate between a panel of expert agents. Your sole "
        "purpose is to synthesize the entire debate into a final, balanced "
        "summary.\n\n"
        'Do not introduce your own opinions, take a side, or declare a "winner." '
        "Your duty is to the user, who needs a clear summary of the "
        "discussion.\n\n"
        "Please structure your response using the following markdown format:\n\n"
        "## Executive Summary\n"
        "A one-paragraph overview of the core tension and the general direction "
        "of the debate.\n\n"
        "## Key Points of Contention\n"
        "Summarize the 2-3 primary areas where the panelists disagreed. For each "
        "point, briefly state the opposing views.\n\n"
        "## Surprising Areas of Agreement\n"
        "Highlight any significant points of consensus or unexpected common "
        "ground reached by the panel.\n\n"
        "## Outstanding Questions\n"
        "Conclude by identifying the most critical unresolved questions or the "
        "fundamental trade-offs that remain. Frame these as questions a "
        "decision-maker would need to answer next."
    ),
    "opening_statement": (
        "Please provide your opening statement on the following topic. Lead with "
        "your strongest, most compelling argument immediately after stating your "
        "position:"
    ),
}
