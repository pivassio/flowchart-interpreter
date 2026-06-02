from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def execute_logic(nodes_map, edges):
    # Спрощена симуляція: виконуємо всі вузли, що мають зв'язки
    shared_vars = {}
    output = []
    
    # Сортуємо вузли (в реалі треба обходити граф, тут для прикладу — послідовно)
    for node_id in nodes_map:
        node = nodes_map[node_id]['data']
        v1 = node.get('v1', 'x')
        v2 = node.get('v2', '0')
        n_type = node.get('type')

        time.sleep(random.uniform(0.0001, 0.001)) # Недетермінізм

        if n_type == "ASSIGN_VAL":
            shared_vars[v1] = int(v2) if v2.isdigit() else 0
        elif n_type == "PRINT":
            output.append(str(shared_vars.get(v1, 0)))
        # Додай тут IF_LT, INPUT тощо...

    return " ".join(output)

@app.post("/run-test")
async def run_test(payload: dict = Body(...)):
    nodes = payload.get('nodes', [])
    edges = payload.get('edges', [])
    k = payload.get('k', 20)
    
    # Знаходимо "голови" потоків (вузли, в які нічого не входить)
    targets = {e['target'] for e in edges}
    heads = [n['id'] for n in nodes if n['id'] not in targets]

    def get_thread_sequence(head_id):
        seq = []
        curr = head_id
        while curr:
            node_data = next((n for n in nodes if n['id'] == curr), None)
            if not node_data: break
            seq.append(node_data['data'])
            # Шукаємо наступний вузол за зв'язком
            next_edge = next((e for e in edges if e['source'] == curr), None)
            curr = next_edge['target'] if next_edge else None
        return seq

    thread_sequences = [get_thread_sequence(h) for h in heads]
    
    # Виконуємо K разів
    all_outputs = []
    for _ in range(k):
        shared_vars = {}
        logs = []
        lock = threading.Lock()

        def run_thread(sequence):
            for cmd in sequence:
                time.sleep(random.uniform(0.001, 0.01)) # Недетермінізм
                v1, v2, t = cmd.get('v1'), cmd.get('v2'), cmd.get('type')
                
                if t == "ASSIGN_VAL": shared_vars[v1] = int(v2) if v2.isdigit() else 0
                elif t == "PRINT": 
                    with lock: logs.append(str(shared_vars.get(v1, 0)))

        threads = [threading.Thread(target=run_thread, args=(s,)) for s in thread_sequences]
        for t in threads: t.start()
        for t in threads: t.join()
        all_outputs.append(" ".join(logs))

    unique = set(all_outputs)
    return {"summary": f"Унікальних результатів: {len(unique)}\nВаріанти: {list(unique)}"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Сервер запускається на http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)