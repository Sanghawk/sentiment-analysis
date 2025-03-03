```
/api
├── .gitignore                # API-specific .gitignore
├── Dockerfile                # Dockerfile for building the FastAPI container
├── requirements.txt          # Python dependencies
├── app
│   ├── __init__.py
│   ├── main.py               # Entry point of the FastAPI app
│   ├── config.py             # App config (reads from environment)
│   ├── database.py           # Database connection logic using SQLAlchemy
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas (request/response models)
│   ├── routers               # Directory for all route (endpoint) modules
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication-related endpoints
│   │   └── articles.py       # Example endpoint for "articles"
│   └── core                  # Additional core utilities (security, etc.)
│       ├── __init__.py
│       └── security.py       # JWT token creation/verification
└── tests                     # Unit / integration tests
    └── test_example.py
```
