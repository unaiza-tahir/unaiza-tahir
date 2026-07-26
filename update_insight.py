"""
Generates a one-line AI/dev insight using Groq's LLM API
and injects it into README.md between the marker comments.

Runs inside a GitHub Action on a schedule — this is the whole
"automation" in the profile: a live LLM call updating a real file.
"""
import os
import re
from groq import Groq

README_PATH = "README.md"
START_MARKER = "<!-- AI-INSIGHT-START -->"
END_MARKER = "<!-- AI-INSIGHT-END -->"

PROMPT = (
    "Write ONE short, sharp, non-cheesy sentence (max 25 words) "
    "that a full-stack AI/agentic-AI developer could put on their "
    "GitHub profile as a daily 'insight'. Topic: LLMs, agentic AI, "
    "software engineering, or automation. No hashtags, no emojis, "
    "no quotation marks, just the sentence."
)


def generate_insight() -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.9,
        max_tokens=60,
    )

    text = response.choices[0].message.content.strip()
    # Safety: strip any stray quotes/newlines the model adds
    text = text.strip('"').strip("'").replace("\n", " ")
    return text


def update_readme(new_line: str) -> None:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        flags=re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{new_line}\n{END_MARKER}"

    if not pattern.search(content):
        raise RuntimeError(
            "Markers not found in README.md — check START/END marker text."
        )

    new_content = pattern.sub(replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    insight = generate_insight()
    print(f"Generated insight: {insight}")
    update_readme(insight)
