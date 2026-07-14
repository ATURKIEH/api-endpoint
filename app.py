from fastapi import FastAPI, HTTPException

app = FastAPI()

to_dos = {"#1":['title1', 'done'], "#2":['title2', 'false'], "#3":['title3', 'done']}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def get_info():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/tasks")
def get_tasks():
    return to_dos

@app.get("/tasks/{id}")
def get_task(id: str):
    task = to_dos.get(id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    else:
        return {"id": id, "title": task[0], "completed": task[1]} 

@app.post("/tasks", status_code=201)
def create_task(title: str):
    id = f"#{len(to_dos) + 1}"
    to_dos[id] = [title, "false"]
    return {"message": "created successfully"}


@app.put("/tasks/{id}")
def update_task(id: str, title: str = None, completed: str = None):
    task = to_dos.get(id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    if title is not None:
        task[0] = title
    if completed is not None:
        task[1] = completed
    return {"message": "updated successfully"}

@app.delete("/tasks/{id}")
def delete_task(id: str):
    task = to_dos.get(id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    del to_dos[id]
    return {"message": "deleted successfully"}