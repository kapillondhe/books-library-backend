from fastapi import FastAPI

app = FastAPI(
    title="Books Library API",
    description="Online Books Library Backend API",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Books Library API is running"}
