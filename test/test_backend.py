from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

test_app=FastAPI()

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@test_app.get("/api/hello")
def hello():
    return {"message": "Hello from backend!"}


#command to run backend: uvicorn test.test_backend:test_app --reload
#command to run frontend: python3 -m http.server 3000 --directory test, then go to http://localhost:3000/test_frontend_index.html