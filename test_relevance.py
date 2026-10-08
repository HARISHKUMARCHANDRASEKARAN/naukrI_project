from relevance import analyze_job


jobs = [
    {
        "title": "GenAI Engineer",
        "description": "Build LLM and RAG applications."
    },
    {
        "title": "AI Software Engineer",
        "description": "Develop Python backend services for artificial intelligence products."
    },
    {
        "title": "Python Developer - AI",
        "description": "Build Python services for an AI platform."
    },
    {
        "title": "Software Engineer - Machine Learning",
        "description": "Build machine learning models and pipelines."
    },
    {
        "title": "Frontend Developer - React",
        "description": "Build React user interfaces and frontend components."
    },
]


for job in jobs:
    result = analyze_job(job)

    print("=" * 60)
    print(f"JOB: {job['title']}")
    print(f"DECISION: {result['decision']}")
    print(f"MATCH SCORE: {result['match_score']}%")
    print(f"REASON: {result['reason']}")

    if result["decision"] == "APPLY":
        print("🚀 Agent will continue to application")
    else:
        print("⏭️ Agent will skip this job")