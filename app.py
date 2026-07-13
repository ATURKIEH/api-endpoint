from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/sum")
def calculate_sum(data: dict):
    result = sum(data.values())
    return {"result": result}