import React, { useState, useCallback } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  applyNodeChanges, 
  applyEdgeChanges,
  Handle, 
  Position 
} from 'reactflow';
import axios from 'axios';
import 'reactflow/dist/style.css';

// 1. ОПИС КОМПОНЕНТА ВУЗЛА 
const ProgramNode = ({ data, id }) => {
  return (
    <div style={{ 
      background: '#fff', padding: '12px', borderRadius: '8px', 
      border: '2px solid #333', width: '200px', position: 'relative'
    }}>
      <Handle type="target" position={Position.Top} />
      
      <button 
        onClick={() => data.onDelete(id)}
        style={{
          position: 'absolute', right: '-10px', top: '-10px',
          background: '#ff4d4d', color: 'white', border: 'none',
          borderRadius: '50%', width: '20px', height: '20px', cursor: 'pointer'
        }}
      >✕</button>

      <div style={{ fontSize: '10px', color: '#888' }}>ID: {id}</div>
      
      <select 
        name="type" 
        onChange={(e) => data.onConfigChange(id, 'type', e.target.value)} 
        value={data.type} 
        style={{ width: '100%', marginBottom: '5px' }}
      >
        <option value="ASSIGN_VAL">V = C (Константа)</option>
        <option value="ASSIGN_VAR">V1 = V2 (Змінна)</option>
        <option value="INPUT">INPUT V</option>
        <option value="PRINT">PRINT V</option>
        <option value="IF_LT">{"IF V < C"}</option>
      </select>

      <input 
        placeholder="Змінна (напр. x)" 
        className="nodrag"
        onChange={(e) => data.onConfigChange(id, 'v1', e.target.value)} 
        value={data.v1 || ''} 
        style={{ width: '100%', fontSize: '12px', marginTop: '4px', padding: '4px', boxSizing: 'border-box' }} 
      />
             
      <input 
        placeholder="Значення / V2" 
        className="nodrag"
        onChange={(e) => data.onConfigChange(id, 'v2', e.target.value)} 
        value={data.v2 || ''} 
        style={{ width: '100%', fontSize: '12px', marginTop: '4px', padding: '4px', boxSizing: 'border-box' }} 
      />
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

// --- 2. РЕЄСТРАЦІЯ ТИПУ ВУЗЛА ---
const nodeTypes = { programNode: ProgramNode };

// --- 3. ГОЛОВНИЙ КОМПОНЕНТ ---
export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback((ch) => setNodes((nds) => applyNodeChanges(ch, nds)), []);
  const onEdgesChange = useCallback((ch) => setEdges((eds) => applyEdgeChanges(ch, eds)), []);
  const onConnect = useCallback((p) => setEdges((eds) => addEdge(p, eds)), []);

  const onConfigChange = (id, name, value) => {
    setNodes((nds) => nds.map((node) => {
      if (node.id === id) {
        return { ...node, data: { ...node.data, [name]: value } };
      }
      return node;
    }));
  };

  const onDeleteNode = (id) => {
    setNodes((nds) => nds.filter((n) => n.id !== id));
    setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
  };

  const addNode = () => {
    const id = `node_${Date.now()}`;
    setNodes((nds) => nds.concat({
      id,
      type: 'programNode',
      position: { x: 100, y: 100 },
      data: { 
        type: 'ASSIGN_VAL', 
        v1: '', 
        v2: '', 
        onConfigChange: onConfigChange, 
        onDelete: onDeleteNode 
      }
    }));
  };

  const runTest = async () => {
    try {
      const res = await axios.post('http://localhost:8000/run-test', { nodes, edges, k: 20 });
      alert(res.data.summary);
    } catch (err) {
      alert("Бекенд не відповідає! Запусти python main.py");
    }
  };

  const generateCode = async () => {
    try {
      const res = await axios.post('http://localhost:8000/generate-code', { nodes, edges });
      console.log("Згенерований код:\n", res.data.code);
      alert("Код згенеровано! Відкрий консоль браузера (F12), щоб його побачити.");
    } catch (err) {
      alert("Помилка при генерації коду.");
    }
  };

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#f0f0f0' }}>
      <div style={{ 
        position: 'absolute', zIndex: 10, padding: '15px', 
        display: 'flex', gap: '10px', background: 'rgba(255,255,255,0.8)',
        width: '100%', borderBottom: '1px solid #ccc'
      }}>
        <button onClick={addNode} style={btnStyle}> Додати блок</button>
        <button onClick={runTest} style={{...btnStyle, background: 'green', color: 'white'}}>Тест </button>
        <button onClick={generateCode} style={{...btnStyle, background: 'blue', color: 'white'}}> Згенерувати .py код</button>
      </div>

      <ReactFlow 
        nodes={nodes} 
        edges={edges} 
        onNodesChange={onNodesChange} 
        onEdgesChange={onEdgesChange} 
        onConnect={onConnect} 
        nodeTypes={nodeTypes} 
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

const btnStyle = { padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', border: '1px solid #999' };