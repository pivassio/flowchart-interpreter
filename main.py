import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import random

# Спільна пам'ять (100 змінних)
shared_vars = [0] * 100

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Flowchart Multi-thread Tool")
        self.threads_data = [] 

        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Button(frame, text="Додати потік", command=self.add_thread).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Запустити все", command=self.run_simulation, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Генерувати код", command=self.generate_python_code).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Стрес-тест", command=self.run_stress_test).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(root)
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.container = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        self.container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def add_thread(self):
        thread_idx = len(self.threads_data)
        self.threads_data.append([]) 
        
        t_frame = tk.LabelFrame(self.container, text=f"Потік №{thread_idx}")
        t_frame.pack(fill="x", padx=10, pady=5)

        columns = ("id", "type", "params", "next")
        tree = ttk.Treeview(t_frame, columns=columns, show="headings", height=5)
        tree.heading("id", text="ID")
        tree.heading("type", text="Тип")
        tree.heading("params", text="Параметри")
        tree.heading("next", text="Наступний")
        tree.pack(side=tk.LEFT)

        tk.Button(t_frame, text="+ Блок", command=lambda: self.add_block(tree, thread_idx)).pack(side=tk.LEFT, padx=5)

    def add_block(self, tree, t_idx):
        cmd_type = simpledialog.askstring("Команда", "Тип: V=C, V1=V2, PRINT, IF").upper()
        if not cmd_type: return

        new_id = len(tree.get_children())
        block = {"id": new_id, "type": cmd_type, "next": new_id + 1}

        if cmd_type == "V=C":
            v = simpledialog.askinteger("Ввід", "V (0-99):", minvalue=0, maxvalue=99)
            c = simpledialog.askinteger("Ввід", "Значення C:")
            block.update({"v": v, "c": c})
            params = f"V[{v}] = {c}"
        elif cmd_type == "PRINT":
            v = simpledialog.askinteger("Ввід", "Вивести V (0-99):", minvalue=0, maxvalue=99)
            block.update({"v": v})
            params = f"Print V[{v}]"
        elif cmd_type == "IF":
            v = simpledialog.askinteger("Ввід", "Змінна V:", minvalue=0, maxvalue=99)
            c = simpledialog.askinteger("Ввід", "Менше за C:")
            if_t = simpledialog.askinteger("Перехід", "ID якщо ТАК:")
            if_f = simpledialog.askinteger("Перехід", "ID якщо НІ:")
            block.update({"v": v, "c": c, "if_true": if_t, "if_false": if_f})
            block["next"] = None
            params = f"V[{v}] < {c} ? {if_t} : {if_f}"
        else:
            messagebox.showwarning("!", "Непідтримуваний тип")
            return

        self.threads_data[t_idx].append(block)
        tree.insert("", "end", values=(new_id, cmd_type, params, block.get("next", "Умова")))

    def run_simulation(self):
        print("\n--- СИМУЛЯЦІЯ ЗАПУЩЕНА ---")
        for i, blocks in enumerate(self.threads_data):
            threading.Thread(target=self.execute, args=(i, blocks), daemon=True).start()

    def execute(self, t_id, blocks):
        curr = 0
        while curr is not None and curr < len(blocks):
            b = next((x for x in blocks if x['id'] == curr), None)
            if not b: break
            
            time.sleep(random.uniform(0.1, 0.5)) # Недетермінованість
            
            if b['type'] == "V=C":
                shared_vars[b['v']] = b['c']
                print(f"[Thread {t_id}] V[{b['v']}] = {b['c']}")
                curr = b['next']
            elif b['type'] == "PRINT":
                print(f">>> [Thread {t_id}] OUTPUT: {shared_vars[b['v']]}")
                curr = b['next']
            elif b['type'] == "IF":
                curr = b['if_true'] if shared_vars[b['v']] < b['c'] else b['if_false']
    
    def generate_python_code(self):
        code = [
            "import threading", "import time", "import random", "",
            "shared_vars = [0] * 100", "",
            "# Автоматично згенеровані функції потоків"
        ]
        
        for i, blocks in enumerate(self.threads_data):
            code.append(f"def thread_{i}():")
            code.append("    curr = 0")
            code.append(f"    while curr is not None and curr < {len(blocks)}:")
            
            for b in blocks:
                code.append(f"        if curr == {b['id']}:")
                if b['type'] == "V=C":
                    code.append(f"            shared_vars[{b['v']}] = {b['c']}; curr = {b['next']}")
                elif b['type'] == "PRINT":
                    code.append(f"            print(f'Thread {i} V[{b['v']}] = {{shared_vars[{b['v']}]}}'); curr = {b['next']}")
                elif b['type'] == "IF":
                    code.append(f"            curr = {b['if_true']} if shared_vars[{b['v']}] < {b['c']} else {b['if_false']}")
            code.append("")

        code.append("threads = []")
        for i in range(len(self.threads_data)):
            code.append(f"t{i} = threading.Thread(target=thread_{i})")
            code.append(f"threads.append(t{i}); t{i}.start()")
        
        with open("generated_code.py", "w", encoding="utf-8") as f:
            f.write("\n".join(code))
        messagebox.showinfo("Успіх", "Пункт 2 виконано: код збережено в generated_code.py")

    def run_stress_test(self):
        K = 10  # Кількість запусків
        unique_results = set()
        
        print(f"\n--- СТРЕС-ТЕСТ ({K} запусків) ---")
        for _ in range(K):
            global shared_vars
            shared_vars = [0] * 100
            threads = [threading.Thread(target=self.execute, args=(i, b)) for i, b in enumerate(self.threads_data)]
            for t in threads: t.start()
            for t in threads: t.join()
            # Фіксуємо результат перших 3-х змінних як "стан"
            unique_results.add(tuple(shared_vars[:3]))
            
        messagebox.showinfo("Пункт 3", f"Тест завершено.\nУнікальних станів пам'яті: {len(unique_results)} з {K}.\nЦе доводить недетермінованість системи.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()