"""
A curated skills dictionary for matching against resume/JD text.
Grouped by category purely for readability - matching is flat across all of them.
Not exhaustive by design: broad enough to catch common CS/SWE resumes,
narrow enough to avoid false positives from generic English words.
"""

SKILLS_DB: dict[str, list[str]] = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#",
        "go", "golang", "rust", "kotlin", "swift", "php", "ruby", "scala",
        "matlab", "sql", "html", "css", "bash", "shell scripting",
    ],
    "frontend": [
        "react", "angular", "vue", "next.js", "nextjs", "redux", "tailwind",
        "bootstrap", "jquery", "webpack", "vite", "sass",
    ],
    "backend": [
        "node.js", "nodejs", "express", "django", "flask", "fastapi",
        "spring boot", "spring", ".net", "asp.net", "rails", "laravel",
        "graphql", "rest api", "grpc", "microservices",
    ],
    "database": [
        "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite",
        "oracle", "cassandra", "dynamodb", "firebase", "elasticsearch",
        "sql server",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "jenkins", "ci/cd", "github actions", "ansible",
        "linux", "nginx", "cloudformation",
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "keras", "nlp", "computer vision", "opencv",
        "pandas", "numpy", "data science", "llm", "langchain",
        "generative ai", "neural networks", "reinforcement learning",
    ],
    "tools": [
        "git", "github", "gitlab", "jira", "postman", "figma", "vs code",
        "intellij", "docker compose", "kafka", "rabbitmq",
    ],
    "concepts": [
        "data structures", "algorithms", "oop", "object-oriented",
        "system design", "agile", "scrum", "tdd", "unit testing",
        "design patterns", "distributed systems", "oauth", "jwt",
    ],
}


def all_skills() -> set[str]:
    return {skill.lower() for group in SKILLS_DB.values() for skill in group}
