import threading
import time
import random

class FlowEngine:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.shared_vars = {}
        self.output_logs = []
        self.lock = threading.Lock()

    def get_thread_sequences(self):
        # Шукаємо вузли, в які нічого не входить
        targets = {e['target'] for e in self.edges}
        heads = [n['id'] for n in self.nodes if n['id'] not in targets]
        
        sequences = []
        for head_id in heads:
            seq = []
            curr = head_id
            while curr:
                node = next((n for n in self.nodes if n['id'] == curr), None)
                if not node: break
                seq.append(node['data'])
                # Наступний вузол за стрілкою
                edge = next((e for e in self.edges if e['source'] == curr), None)
                curr = edge['target'] if edge else None
            sequences.append(seq)
        return sequences

    def run_single_test(self):
        self.shared_vars = {}
        self.output_logs = []
        sequences = self.get_thread_sequences()
        
        def worker(seq):
            for cmd in seq:
                # Симуляція недетермінізму
                time.sleep(random.uniform(0.001, 0.02))
                
                t = cmd.get('type')
                v1 = cmd.get('v1', '').strip()
                v2 = cmd.get('v2', '').strip()

                if t == "ASSIGN_VAL":
                    self.shared_vars[v1] = int(v2) if v2.isdigit() else 0
                elif t == "ASSIGN_VAR":
                    self.shared_vars[v1] = self.shared_vars.get(v2, 0)
                elif t == "INPUT":
                    # Для тесту симулюємо ввід випадковим числом або 0
                    self.shared_vars[v1] = random.randint(0, 100)
                elif t == "PRINT":
                    val = self.shared_vars.get(v1, 0)
                    with self.lock:
                        self.output_logs.append(str(val))
                elif t == "IF_LT":
                    # Якщо умова не виконується, перериваємо цей потік
                    val = self.shared_vars.get(v1, 0)
                    limit = int(v2) if v2.isdigit() else 0
                    if not (val < limit): break

        threads = [threading.Thread(target=worker, args=(s,)) for s in sequences]
        for t in threads: t.start()
        for t in threads: t.join()
        return " ".join(self.output_logs)

    def generate_python_source(self):
        sequences = self.get_thread_sequences()
        code = ["import threading, time, random", "shared_vars = {}", "lock = threading.Lock()\n"]
        
        for i, seq in enumerate(sequences):
            code.append(f"def thread_{i}():")
            for cmd in seq:
                t, v1, v2 = cmd['type'], cmd['v1'], cmd['v2']
                code.append(f"    time.sleep(random.uniform(0.001, 0.01))")
                if t == "ASSIGN_VAL": code.append(f"    shared_vars['{v1}'] = {v2}")
                if t == "PRINT": code.append(f"    with lock: print(shared_vars.get('{v1}', 0))")
            code.append("")
        
        code.append("ts = [" + ",".join([f"threading.Thread(target=thread_{i})" for i in range(len(sequences))]) + "]")
        code.append("for t in ts: t.start()\nfor t in ts: t.join()")
        return "\n".join(code)