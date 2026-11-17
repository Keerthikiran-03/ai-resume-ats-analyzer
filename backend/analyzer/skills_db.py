"""
Comprehensive Taxonomy of Skills, Action Verbs, and Resume Section Markers.
Used for multi-dimensional ATS extraction and scoring.
"""

SKILLS_TAXONOMY = {
    # Programming Languages
    "python": "Languages",
    "javascript": "Languages",
    "typescript": "Languages",
    "java": "Languages",
    "c++": "Languages",
    "c#": "Languages",
    "c": "Languages",
    "go": "Languages",
    "golang": "Languages",
    "rust": "Languages",
    "ruby": "Languages",
    "php": "Languages",
    "swift": "Languages",
    "kotlin": "Languages",
    "scala": "Languages",
    "r": "Languages",
    "matlab": "Languages",
    "dart": "Languages",
    "shell": "Languages",
    "bash": "Languages",
    "powershell": "Languages",
    "sql": "Languages",
    "html": "Languages",
    "html5": "Languages",
    "css": "Languages",
    "css3": "Languages",
    "sass": "Languages",

    # Web & Frontend Frameworks
    "react": "Frontend",
    "react.js": "Frontend",
    "reactjs": "Frontend",
    "next.js": "Frontend",
    "nextjs": "Frontend",
    "vue": "Frontend",
    "vue.js": "Frontend",
    "angular": "Frontend",
    "svelte": "Frontend",
    "tailwind": "Frontend",
    "tailwindcss": "Frontend",
    "bootstrap": "Frontend",
    "redux": "Frontend",
    "webpack": "Frontend",
    "vite": "Frontend",
    "graphql": "Frontend",

    # Backend Frameworks
    "node.js": "Backend",
    "nodejs": "Backend",
    "express": "Backend",
    "express.js": "Backend",
    "fastapi": "Backend",
    "flask": "Backend",
    "django": "Backend",
    "spring": "Backend",
    "spring boot": "Backend",
    "asp.net": "Backend",
    ".net": "Backend",
    ".net core": "Backend",
    "ruby on rails": "Backend",
    "rails": "Backend",
    "nest.js": "Backend",
    "nestjs": "Backend",
    "rest api": "Backend",
    "restful apis": "Backend",
    "grpc": "Backend",
    "microservices": "Backend",
    "websocket": "Backend",

    # Databases & Storage
    "postgresql": "Databases",
    "postgres": "Databases",
    "mysql": "Databases",
    "mongodb": "Databases",
    "redis": "Databases",
    "sqlite": "Databases",
    "cassandra": "Databases",
    "elasticsearch": "Databases",
    "dynamodb": "Databases",
    "neo4j": "Databases",
    "mariadb": "Databases",
    "snowflake": "Databases",
    "bigquery": "Databases",
    "supabase": "Databases",
    "firebase": "Databases",

    # Cloud & DevOps
    "aws": "Cloud & DevOps",
    "amazon web services": "Cloud & DevOps",
    "azure": "Cloud & DevOps",
    "microsoft azure": "Cloud & DevOps",
    "gcp": "Cloud & DevOps",
    "google cloud": "Cloud & DevOps",
    "docker": "Cloud & DevOps",
    "kubernetes": "Cloud & DevOps",
    "k8s": "Cloud & DevOps",
    "terraform": "Cloud & DevOps",
    "ansible": "Cloud & DevOps",
    "jenkins": "Cloud & DevOps",
    "ci/cd": "Cloud & DevOps",
    "github actions": "Cloud & DevOps",
    "gitlab": "Cloud & DevOps",
    "linux": "Cloud & DevOps",
    "nginx": "Cloud & DevOps",
    "prometheus": "Cloud & DevOps",
    "grafana": "Cloud & DevOps",

    # AI, ML & Data Science
    "machine learning": "AI / Data Science",
    "deep learning": "AI / Data Science",
    "artificial intelligence": "AI / Data Science",
    "data science": "AI / Data Science",
    "nlp": "AI / Data Science",
    "natural language processing": "AI / Data Science",
    "computer vision": "AI / Data Science",
    "tensorflow": "AI / Data Science",
    "pytorch": "AI / Data Science",
    "keras": "AI / Data Science",
    "scikit-learn": "AI / Data Science",
    "pandas": "AI / Data Science",
    "numpy": "AI / Data Science",
    "opencv": "AI / Data Science",
    "huggingface": "AI / Data Science",
    "transformers": "AI / Data Science",
    "llm": "AI / Data Science",
    "llms": "AI / Data Science",
    "large language models": "AI / Data Science",
    "genai": "AI / Data Science",
    "generative ai": "AI / Data Science",
    "rag": "AI / Data Science",
    "langchain": "AI / Data Science",
    "llamaindex": "AI / Data Science",
    "gemini": "AI / Data Science",
    "openai": "AI / Data Science",
    "data analysis": "AI / Data Science",
    "tableau": "AI / Data Science",
    "power bi": "AI / Data Science",

    # Management, Methodologies & Product
    "agile": "Methodologies & Management",
    "scrum": "Methodologies & Management",
    "kanban": "Methodologies & Management",
    "jira": "Methodologies & Management",
    "confluence": "Methodologies & Management",
    "product management": "Methodologies & Management",
    "project management": "Methodologies & Management",
    "sdlc": "Methodologies & Management",
    "okrs": "Methodologies & Management",
    "kpis": "Methodologies & Management",
    "git": "Tools & Version Control",
    "github": "Tools & Version Control",
    "bitbucket": "Tools & Version Control",

    # Soft Skills
    "leadership": "Soft Skills",
    "communication": "Soft Skills",
    "collaboration": "Soft Skills",
    "problem solving": "Soft Skills",
    "critical thinking": "Soft Skills",
    "teamwork": "Soft Skills",
    "mentoring": "Soft Skills",
    "mentorship": "Soft Skills",
    "adaptability": "Soft Skills",
    "time management": "Soft Skills",
    "cross-functional": "Soft Skills",
    "stakeholder management": "Soft Skills",
    "negotiation": "Soft Skills",
    "strategic thinking": "Soft Skills",
    "conflict resolution": "Soft Skills",
    "ownership": "Soft Skills"
}

# High-impact power action verbs recommended by top ATS & recruiters (Google/Harvard/McKinsey)
STRONG_ACTION_VERBS = {
    "spearheaded", "architected", "engineered", "orchestrated", "transformed",
    "accelerated", "maximized", "optimized", "streamlined", "devised",
    "pioneered", "implemented", "delivered", "executed", "generated",
    "negotiated", "surpassed", "automated", "mentored", "empowered",
    "formulated", "established", "directed", "championed", "curated",
    "scaled", "overhauled", "cultivated", "modernized", "designed",
    "authored", "boosted", "consolidated", "reduced", "expanded",
    "integrated", "mobilized", "yielded", "revolutionized", "benchmarked"
}

# Weak, passive, or overused verbs that weaken resume bullets
WEAK_ACTION_VERBS = {
    "worked on", "assisted with", "helped", "was responsible for",
    "handled", "participated in", "tried to", "supported", "attempted",
    "involved in", "dealt with", "utilized", "did", "made", "tasked with"
}

# Standard resume section headers
SECTION_PATTERNS = {
    "contact": [
        r"\bcontact\b", r"\bemail\b", r"\bphone\b", r"\blinkedin\b", r"\bgithub\b"
    ],
    "summary": [
        r"\bprofessional summary\b", r"\bsummary\b", r"\bprofile\b",
        r"\babout me\b", r"\bexecutive summary\b", r"\bcareer objective\b", r"\bobjective\b"
    ],
    "experience": [
        r"\bwork experience\b", r"\bprofessional experience\b", r"\bexperience\b",
        r"\bemployment history\b", r"\bcareer history\b", r"\bwork history\b"
    ],
    "education": [
        r"\beducation\b", r"\bacademic background\b", r"\bacademic history\b",
        r"\bqualifications\b", r"\bdegrees\b"
    ],
    "skills": [
        r"\bskills\b", r"\btechnical skills\b", r"\bcore competencies\b",
        r"\btechnologies\b", r"\bkey skills\b", r"\bexpertise\b", r"\btools\b"
    ],
    "projects": [
        r"\bprojects\b", r"\bkey projects\b", r"\bpersonal projects\b",
        r"\bselected projects\b", r"\bportfolio\b"
    ],
    "certifications": [
        r"\bcertifications\b", r"\bcertificates\b", r"\blicenses\b",
        r"\baccreditations\b", r"\bcertified\b"
    ]
}
