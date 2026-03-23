from fastapi import FastAPI

app = FastAPI(title="Decision Intelligence Console API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
