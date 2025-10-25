'use client'
import { useState } from 'react';
import { Card } from "@/components/aily/Card";
import { Mermaid } from "mermaid";

const Component = () => {
  const [params, setParams] = useState({
    modelSize: 'medium',
    agentCount: 4,
    dataFlow: 'complex'
  });

  const mermaidDiagram = `
graph TD
  subgraph 数据接入层
    A[实验室业务系统] --> B[iDLM工业大模型]
    C[科研数据库] --> B
    D[实验仪器数据] --> B
  end

  subgraph iDLM大模型层
    B --> E[预训练模型]
    B --> F[领域微调模型]
    B --> G[知识图谱]
  end

  subgraph Agentic系统层
    E --> H[数据清洗Agent]
    F --> I[信息抽取Agent]
    G --> J[知识推理Agent]
    H --> K[报告生成Agent]
    I --> K
    J --> K
  end

  subgraph 应用层
    K --> L[论文生成]
    K --> M[专利撰写]
    K --> N[标准制定]
  end

  style A fill:#f9f,stroke:#333,stroke-width:2px
  style B fill:#ff9,stroke:#333,stroke-width:2px
  style K fill:#9f9,stroke:#333,stroke-width:2px
  style L fill:#6cf,stroke:#333,stroke-width:2px
`;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-center mb-8">国家重点实验室智能解决方案技术架构</h1>
      
      <Card className="mb-6 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block mb-2 font-medium">大模型规模</label>
            <select 
              className="w-full p-2 border rounded"
              value={params.modelSize}
              onChange={e => setParams({...params, modelSize: e.target.value})}
            >
              <option value="small">基础版</option>
              <option value="medium">标准版</option>
              <option value="large">高级版</option>
            </select>
          </div>
          
          <div>
            <label className="block mb-2 font-medium">Agent数量</label>
            <input 
              type="range" 
              min="1" 
              max="8" 
              value={params.agentCount}
              onChange={e => setParams({...params, agentCount: parseInt(e.target.value)})}
              className="w-full"
            />
            <div className="text-center">{params.agentCount}个智能体</div>
          </div>
          
          <div>
            <label className="block mb-2 font-medium">数据流复杂度</label>
            <select 
              className="w-full p-2 border rounded"
              value={params.dataFlow}
              onChange={e => setParams({...params, dataFlow: e.target.value})}
            >
              <option value="simple">简单</option>
              <option value="medium">中等</option>
              <option value="complex">复杂</option>
            </select>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4 h-[600px]">
          <Mermaid 
            value={mermaidDiagram}
            className="w-full h-full"
          />
        </div>
      </Card>
    </div>
  );
};

export default Component;