from question_answerer import answer_question


questions = [
    "What is your total years of experience?",
    "What is your current role?",
    "What are your primary technical skills?",
    "Are you willing to relocate?",
    "What is your expected CTC?"
]


for question in questions:
    result = answer_question(question)

    print("=" * 60)
    print("QUESTION:", question)
    print("ANSWER:", result["answer"])
    print("STATUS:", result["status"])