import React, { useState, useCallback } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  Handle, 
  Position,
  applyNodeChanges,
  applyEdgeChanges,
  getIncomers // допомагає знайти вхідні вузли
} from 'reactflow';
import axios from 'axios';
import 'reactflow/dist/style.css';

// --- ОНОВЛЕНИЙ КАСТОМНИЙ БЛОК ---
const ProgramNode = ({ data, id }) => {
  return (
    <div style={{ 
      background: '#fff', padding: '12px', borderRadius: '8px', 
      border: '2px solid #333', width: '200px', position: 'relative'
    }}>
      <Handle type="target" position={Position.Top} />
      
      {/* Кнопка видалення прямо на блоці */}
      <button 
        onClick={() => data.onDelete(id)}
        style={{
          position: 'absolute', right: '-10px', top: '-10px',
          background: '#ff4d4d', color: 'white', border: 'none',
          borderRadius: '50%', width: '20px', height: '20px', cursor: 'pointer'
        }}
      >✕</button>

      <div style={{ fontSize: '10px', color: '#888' }}>ID: {id}</div>
      
      <select name="type" onChange={(e) => data.onConfigChange(id, 'type', e.target.value)} 
              value={data.type} style={{ width: '100%', marginBottom: '5px' }}>
        <option value="ASSIGN_VAL">V = C</option>
        <option value="ASSIGN_VAR">V1 = V2</option>
        <option value="INPUT">INPUT V</option>
        <option value="PRINT">PRINT V</option>
        <option value="IF_LT">{"IF V < C"}</option>
      </select>

      <input name="v1" placeholder="Змінна" className="nodrag"
             onChange={(e) => data.onConfigChange(id, 'v1', e.target.value)} 
             value={data.v1} style={inputStyle} />
             
      <input name="v2" placeholder="Значення" className="nodrag"
             onChange={(e) => data.onConfigChange(id, 'v2', e.target.value)} 
             value={data.v2} style={inputStyle} />
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

const inputStyle = { width: '100%', fontSize: '12px', marginTop: '4px', padding: '4px', boxSizing: 'border-box' };
const nodeTypes = { programNode: ProgramNode };

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback((ch) => setNodes((nds) => applyNodeChanges(ch, nds)), []);
  const onEdgesChange = useCallback((ch) => setEdges((eds) => applyEdgeChanges(ch, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // Функція видалення вузла
  const onDeleteNode = useCallback((id) => {
    setNodes((nds) => nds.filter((node) => node.id !== id));
    setEdges((eds) => eds.filter((edge) => edge.source !== id && edge.target !== id));
  }, []);

  const onConfigChange = (id, name, value) => {
    setNodes((nds) => nds.map((node) => {
      if (node.id === id) {
        return { ...node, data: { ...node.data, [name]: value } };
      }
      return node;
    }));
  };

  const addNode = () => {
    const id = `node_${Date.now()}`;
    setNodes((nds) => nds.concat({
      id,
      type: 'programNode',
      position: { x: 100, y: 100 },
      data: { type: 'ASSIGN_VAL', v1: '', v2: '', onConfigChange, onDelete: onDeleteNode }
    }));
  };

  const startTest = async () => {
    try {
      // Передаємо на бекенд і вузли, і зв'язки (edges)
      const res = await axios.post('http://localhost:8000/run-test', { nodes, edges, k: 20 });
      alert(res.data.summary);
    } catch (err) {
      alert("Бекенд не відповідає");
    }
  };

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <div style={{ position: 'absolute', zIndex: 10, padding: '15px', display: 'flex', gap: '10px' }}>
        <button onClick={addNode} style={btnStyle}>➕ Додати блок</button>
        <button onClick={startTest} style={{...btnStyle, background: '#4CAF50', color: '#fff'}}>🚀 ТЕСТ (K=20)</button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        deleteKeyCode={["Backend", "Delete"]} // Дозволяє видаляти клавішами
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

const btnStyle = { padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', border: '1px solid #ccc' };