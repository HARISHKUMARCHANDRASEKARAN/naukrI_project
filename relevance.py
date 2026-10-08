import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


def analyze_job(job):
    title = job.get("title", "")
    description = job.get("description", "")

    prompt = f"""
Analyze this job for an AI Engineer job application system.

JOB TITLE:
{title}

JOB DESCRIPTION:
{description}

Determine whether this job is broadly related to:

- Artificial Intelligence
- Machine Learning
- Deep Learning
- Generative AI
- LLMs
- RAG
- NLP
- Computer Vision
- AI Agents
- MLOps
- AI Engineering
- AI Software Engineering
- AI-based intelligent automation

Rules:

1. If the job is broadly AI-related, decision MUST be APPLY.
2. Completely unrelated jobs must be SKIP.
3. Match score is informational only.
4. Do not reject an AI-related job because of a low skill match.

Return ONLY valid JSON.

Format:

{{
    "decision": "APPLY",
    "match_score": 92,
    "reason": "Short explanation"
}}

decision must be exactly APPLY or SKIP.
match_score must be an integer from 0 to 100.
"""

    response = llm.invoke(prompt)

    result = json.loads(response.content)

    return result