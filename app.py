from fastapi import FastAPI, HTTPException
import psycopg
from dotenv import load_dotenv
import os
import redis

app = FastAPI()
load_dotenv()
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, decode_responses=True)
class TaskRepo:
    def __init__(self):
        self.to_dos = {"#1":['title1', 'done'], "#2":['title2', 'false'], "#3":['title3', 'done']}

    def get_all(self):
        return self.to_dos
    
    def get_by_id(self, id):
        return self.to_dos.get(id)
    
    def create(self, title):
        id = f"#{len(self.to_dos) + 1}"
        self.to_dos[id] = [title, 'false']

    def update(self, id, title, completed):
        task = self.to_dos.get(id)
        if not task:
            return None
        if title is not None:
            task[0] = title
        if completed is not None:
            task[1] = completed

    def delete(self, id):
        task = self.to_dos.get(id)
        if not task:
            return None
        del self.to_dos[id]



class PostgresTaskRepo:
    
    def __init__(self):
        load_dotenv()
        try:
            self.conn = psycopg.connect(os.environ.get('DATABASE_URL'))

            self.cur= self.conn.cursor()
            self.cur.execute('SELECT version();')
            self.db_version = self.cur.fetchone()
            print(f"Connected successfully! Server version: {self.db_version[0]}")

        except Exception as error:
            print(f'Database error: {error}')

        

    def get_all(self):
        self.cur.execute('SELECT id, title, completed FROM task;')
        rows = self.cur.fetchall()
        result_dict = {row[0]: [row[1], row[2]] for row in rows}
        return result_dict
    
    def get_by_id(self, id):
        self.cur.execute('SELECT title, completed FROM task WHERE id = %s;', (id,))
        return self.cur.fetchone()
    
    def create(self, title):
        self.cur.execute('INSERT INTO task (title, completed) VALUES (%s,%s) RETURNING id;', (title, 'false'))
        self.conn.commit()
    
    def update(self, id, title, completed):
        if title is not None:
            self.cur.execute('UPDATE task SET title = %s WHERE id = %s;',  (title, id))
        if completed is not None:
            self.cur.execute('UPDATE task SET completed = %s WHERE id = %s;',  (completed, id))

        self.conn.commit()

    def delete(self, id):
        self.cur.execute('DELETE FROM task WHERE id = %s;', (id,))
        self.conn.commit()
    


repo = PostgresTaskRepo()


@app.get("/ping-redis")
def ping_redis():
    try:
        redis_client.ping()
        return {"redis": "pong"}
    except Exception as error:
        return {"redis": "unreachable", "error": str(error)}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def get_info():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/tasks")
def get_tasks():
    return repo.get_all()

@app.get("/tasks/{id}")
def get_task(id: str):
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    else:
        return {"id": id, "title": task[0], "completed": task[1]} 

@app.post("/tasks", status_code=201)
def create_task(title: str):
    repo.create(title)
    return {"message": "created successfully"}


@app.put("/tasks/{id}")
def update_task(id: str, title: str = None, completed: str = None):
    repo.update(id, title, completed)
    return {"message": "updated successfully"}

@app.delete("/tasks/{id}")
def delete_task(id: str):
    repo.delete(id)
    return {"message": "deleted successfully"}