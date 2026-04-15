from fastapi import FastAPI

from app.vlm.router import router as vlm_router

from app.api.endpoints.bounding_boxes import router as bounding_boxes_router


app = FastAPI(title="Disaster Assessment Chatbot API")
app = FastAPI()
app.include_router(vlm_router)


@app.get("/greet/{name}")
def greet_user(name: str):
    greetings = ["Hello", "Hi", "Hey", "Greetings", "Howdy", "Salutations"]
    greeting = random.choice(greetings)
    return {"message": f"{greeting}, {name}!"}

@app.get("/time")
def get_time():
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    return {"current_time": time_str}

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(bounding_boxes_router, prefix="/api/bounding-boxes", tags=["bounding-boxes"])
@app.get("/health")
def health():
    return {"status": "ok"}
