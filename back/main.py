from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from engine import FlowEngine # Імпортуємо наш двигун

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/run-test")
async def run_test(payload: dict = Body(...)):
    nodes = payload.get('nodes', [])
    edges = payload.get('edges', [])
    k = payload.get('k', 20)
    
    engine = FlowEngine(nodes, edges)
    results = [engine.run_single_test() for _ in range(k)]
    
    unique = set(results)
    return {
        "summary": f"Унікальних варіантів: {len(unique)}\nРезультати: {list(unique)}"
    }

@app.post("/generate-code")
async def get_code(payload: dict = Body(...)):
    engine = FlowEngine(payload.get('nodes', []), payload.get('edges', []))
    return {"code": engine.generate_python_source()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)