from relevance import analyze_job


jobs = [
    {
        "title": "GenAI Engineer",
        "company": "Example AI Company",
        "description": """
        Build and maintain LLM and RAG applications.
        Work with Python, LangChain, vector databases and AI agents.
        """
    },
    {
        "title": "Python Developer - AI",
        "company": "Example Tech Company",
        "description": """
        Develop Python services for an AI platform.
        Work with APIs and backend systems.
        """
    },
    {
        "title": "Frontend Developer - React",
        "company": "Example Web Company",
        "description": """
        Build React user interfaces and frontend components.
        Work with JavaScript, HTML and CSS.
        """
    }
]


def process_jobs():
    for job in jobs:
        result = analyze_job(job)

        print("=" * 60)
        print(f"JOB: {job['title']}")
        print(f"COMPANY: {job['company']}")
        print(f"DECISION: {result['decision']}")
        print(f"MATCH SCORE: {result['match_score']}%")
        print(f"REASON: {result['reason']}")

        if result["decision"] == "APPLY":
            print("🚀 → Continue to application")
        else:
            print("⏭️ → Skip this job")


if __name__ == "__main__":
    process_jobs()