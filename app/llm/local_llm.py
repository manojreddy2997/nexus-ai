import ollama


MODEL_NAME = "llama3.2:3b"

DEFAULT_SYSTEM_PROMPT = (
    "You are Nexus AI, a helpful assistant. "
    "Explain concepts clearly and honestly. "
    "Do not invent facts when you do not know the answer."
)


def generate_response(
    user_message: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model_name: str = MODEL_NAME,
) -> str:
    """Send a message to the local LLM and return its response."""

    if not user_message or not user_message.strip():
        raise ValueError("user_message cannot be empty.")

    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    return response.message.content
