import json
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from profile_loader import load_profile


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


# ============================================================
# AI / ML / GENAI TECHNOLOGY DETECTION
# ============================================================

AI_TECHNOLOGIES = {
    "python",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "generative ai",
    "genai",
    "llm",
    "llms",
    "large language model",
    "large language models",
    "rag",
    "retrieval augmented generation",
    "langchain",
    "langgraph",
    "ai agents",
    "agentic ai",
    "agents",
    "transformers",
    "hugging face",
    "huggingface",
    "nlp",
    "natural language processing",
    "computer vision",
    "cnn",
    "rnn",
    "lstm",
    "gru",
    "pytorch",
    "tensorflow",
    "keras",
    "scikit-learn",
    "sklearn",
    "numpy",
    "pandas",
    "pyspark",
    "vector database",
    "vector databases",
    "embeddings",
    "semantic search",
    "chroma",
    "chromadb",
    "faiss",
    "pinecone",
    "milvus",
    "qdrant",
    "mcp",
    "model context protocol",
    "google adk",
    "adk",
    "ollama",
    "openai",
    "gemini",
    "claude",
    "groq",
    "mistral",
    "prompt engineering",
    "prompt engineering",
    "fine tuning",
    "fine-tuning",
    "mlops",
    "aws bedrock",
    "azure ai",
}


# ============================================================
# EXTRACT TECHNOLOGY FROM QUESTION
# ============================================================

def extract_technology(question):
    """
    Ask the LLM to identify the technology mentioned
    in an experience-related question.
    """

    prompt = f"""
Identify the main technology, framework, platform, or
technical skill mentioned in this recruiter question.

QUESTION:
{question}

Return ONLY valid JSON.

Format:

{{
    "technology": "technology name",
    "is_technology_question": true
}}

If this is not a technology experience question:

{{
    "technology": "",
    "is_technology_question": false
}}
"""

    response = llm.invoke(prompt)

    return json.loads(response.content)


# ============================================================
# NORMALIZE TECHNOLOGY NAME
# ============================================================

def normalize_technology(technology):

    technology = technology.lower().strip()

    aliases = {
        "google adk": "google adk",
        "adk": "google adk",

        "huggingface": "hugging face",

        "sklearn": "scikit-learn",

        "gen ai": "generative ai",
        "genai": "generative ai",

        "large language models": "llms",
        "large language model": "llm",

        "vector db": "vector database",
        "vector databases": "vector database",
    }

    return aliases.get(
        technology,
        technology
    )


# ============================================================
# FIND ACTUAL EXPERIENCE
# ============================================================

def find_actual_experience(
    technology,
    profile
):

    skill_experience = profile.get(
        "skill_experience",
        {}
    )

    normalized = normalize_technology(
        technology
    )

    # --------------------------------------------------------
    # Check exact / normalized skill
    # --------------------------------------------------------

    for skill, years in skill_experience.items():

        normalized_skill = normalize_technology(
            skill
        )

        if normalized_skill == normalized:

            return years

    # --------------------------------------------------------
    # Check skills list
    # --------------------------------------------------------

    skills = profile.get(
        "skills",
        []
    )

    for skill in skills:

        normalized_skill = normalize_technology(
            skill
        )

        if normalized_skill == normalized:

            # Skill exists but exact experience
            # wasn't provided.
            return profile.get(
                "experience_years",
                0
            )

    return None


# ============================================================
# CHECK WHETHER TECHNOLOGY IS AI RELATED
# ============================================================

def is_ai_related_technology(
    technology
):

    technology = normalize_technology(
        technology
    )

    # Exact match
    if technology in AI_TECHNOLOGIES:
        return True

    # Partial match
    for ai_technology in AI_TECHNOLOGIES:

        if (
            ai_technology in technology
            or technology in ai_technology
        ):
            return True

    return False


# ============================================================
# ANSWER TECHNOLOGY EXPERIENCE
# ============================================================

def answer_technology_question(
    question,
    technology,
    profile
):

    # --------------------------------------------------------
    # First: check actual profile experience
    # --------------------------------------------------------

    actual_years = find_actual_experience(
        technology,
        profile
    )

    if actual_years is not None:

        return {
            "answer": f"{actual_years} years",
            "status": "KNOWN",
            "source": "profile"
        }

    # --------------------------------------------------------
    # Unknown but AI-related technology
    # --------------------------------------------------------

    if is_ai_related_technology(
        technology
    ):

        return {
            "answer": "1 year",
            "status": "KNOWN",
            "source": "related_ai_technology"
        }

    # --------------------------------------------------------
    # Unrelated / unknown technology
    # --------------------------------------------------------

    return {
        "answer": "",
        "status": "UNKNOWN",
        "source": "not_available"
    }


# ============================================================
# GENERAL PROFILE QUESTION
# ============================================================

def answer_general_question(
    question,
    profile
):

    prompt = f"""
You are an AI job application assistant.

Answer the recruiter question using ONLY the
candidate profile.

CANDIDATE PROFILE:
{json.dumps(profile, indent=2)}

QUESTION:
{question}

Rules:

1. Use information from the candidate profile.
2. Understand the meaning of the question, not just
   exact keyword matches.
3. Keep the answer short and suitable for a job application.
4. Do not invent personal information.
5. Do not invent salary, location, notice period,
   education, employment authorization, or other
   personal information.
6. If the profile does not contain enough information,
   return UNKNOWN.

Return ONLY valid JSON:

{
    "answer": "answer here",
    "status": "KNOWN"
}

OR:

{
    "answer": "",
    "status": "UNKNOWN"
}
"""

    response = llm.invoke(prompt)

    return json.loads(
        response.content
    )


# ============================================================
# MAIN QUESTION ANSWERER
# ============================================================

def answer_question(question):

    profile = load_profile()

    question = question.strip()

    if not question:

        return {
            "answer": "",
            "status": "UNKNOWN",
            "source": "empty_question"
        }

    # --------------------------------------------------------
    # Ask LLM what kind of question this is
    # --------------------------------------------------------

    try:

        classification = extract_technology(
            question
        )

    except Exception as error:

        print(
            "Question classification error:",
            error
        )

        classification = {
            "technology": "",
            "is_technology_question": False
        }

    # --------------------------------------------------------
    # Technology experience question
    # --------------------------------------------------------

    if classification.get(
        "is_technology_question"
    ):

        technology = classification.get(
            "technology",
            ""
        ).strip()

        if technology:

            result = answer_technology_question(
                question,
                technology,
                profile
            )

            result["technology"] = technology

            return result

    # --------------------------------------------------------
    # General recruiter question
    # --------------------------------------------------------

    try:

        result = answer_general_question(
            question,
            profile
        )

        return result

    except Exception as error:

        print(
            "General question error:",
            error
        )

        return {
            "answer": "",
            "status": "UNKNOWN",
            "source": "llm_error"
        }
    