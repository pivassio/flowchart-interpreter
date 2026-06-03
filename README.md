# 🛠 Multi-threaded Flowchart Visualizer & Transpiler

A specialized tool for visual programming and testing of multi-threaded algorithms. Developed as a university lab assignment.

##  Core Features

- **Visual Programming Interface (Requirement 1):** Create, edit, and connect flowchart blocks for up to 100 threads using a React-based GUI.
- **Source Code Translation (Requirement 2):** Automatically translate visual flowcharts into executable Python source code utilizing the `threading` library.
- **Non-determinism Analysis :** Run automated testing (K=20) to detect race conditions and display all unique execution outcomes.

##  System Architecture

The project follows a modern Client-Server architecture:

1.  **Frontend (React + React Flow):** An interactive canvas where users build directed graphs representing thread logic.
2.  **Backend (FastAPI + Python):** A custom-built **Flow Engine** that parses graph topology, generates Python code, and executes multi-threaded simulations.
3.  **Shared Memory Simulation:** Implements a global variable dictionary (`shared_vars`) accessible across all concurrent threads.

##  Tech Stack

- **Frontend:** React.js, React Flow, Axios.
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Threading.

##  Getting Started

### 1. Start the Backend
```bash
cd backend
pip install fastapi uvicorn
python main.py

### 2. Start the Frontend
cd frontend
npm install
npm run dev