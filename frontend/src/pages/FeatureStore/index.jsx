import React, { useState } from 'react';
import AddFeatureModal from './AddFeatureModal';
import EditFeatureModal from './EditFeatureModal';
import DeleteFeatureModal from './DeleteFeatureModal';
import FeatureDetailModal from './FeatureDetailModal';

// mock特征数据，后续可对接API
const mockFeatures = [
  { id: 1, name: '动量因子', type: '数值', version: 'v1.0', created_by: 'Alice', created_at: '2024-01-01', status: 'active', description: '近20日收益率', lineage: 'price->return->momentum' },
  { id: 2, name: '市盈率', type: '数值', version: 'v1.1', created_by: 'Bob', created_at: '2024-01-10', status: 'active', description: '市值/净利润', lineage: 'market_cap->net_income->pe' },
  { id: 3, name: '行业哑变量', type: '分类', version: 'v1.0', created_by: 'Carol', created_at: '2024-01-15', status: 'inactive', description: '行业one-hot', lineage: 'industry->onehot' },
];

export default function FeatureStorePage() {
  // 特征列表、弹窗状态
  const [features, setFeatures] = useState(mockFeatures);
  const [showAdd, setShowAdd] = useState(false);
  const [editFeature, setEditFeature] = useState(null);
  const [deleteFeature, setDeleteFeature] = useState(null);
  const [detailFeature, setDetailFeature] = useState(null);

  return (
    <div style={{padding:24}}>
      <h2>特征工程平台</h2>
      {/* 新增特征按钮 */}
      <button onClick={()=>setShowAdd(true)} style={{marginBottom:16}}>新增特征</button>
      {/* 特征列表表格 */}
      <table style={{width:'100%',background:'#111',color:'#fff',borderRadius:8}}>
        <thead>
          <tr>
            <th>ID</th>
            <th>特征名称</th>
            <th>类型</th>
            <th>版本</th>
            <th>创建人</th>
            <th>创建时间</th>
            <th>状态</th>
            <th>描述</th>
            <th>血缘</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {features.map(f => (
            <tr key={f.id}>
              <td>{f.id}</td>
              <td style={{cursor:'pointer',color:'#4fd6ff'}} onClick={()=>setDetailFeature(f)}>{f.name}</td>
              <td>{f.type}</td>
              <td>{f.version}</td>
              <td>{f.created_by}</td>
              <td>{f.created_at}</td>
              <td>{f.status === 'active' ? '启用' : '停用'}</td>
              <td>{f.description}</td>
              <td>{f.lineage}</td>
              <td>
                <button onClick={()=>setEditFeature(f)}>编辑</button>
                <button style={{marginLeft:8}} onClick={()=>setDeleteFeature(f)}>删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* 新增特征弹窗 */}
      {showAdd && <AddFeatureModal onClose={()=>setShowAdd(false)} onAdd={item=>{
        setFeatures(f=>[...f, { ...item, id: f.length ? Math.max(...f.map(x=>x.id))+1 : 1 }]);
      }} />}
      {/* 编辑特征弹窗 */}
      {editFeature && <EditFeatureModal feature={editFeature} onClose={()=>setEditFeature(null)} onEdit={item=>{
        setFeatures(f=>f.map(x=>x.id===item.id ? item : x));
      }} />}
      {/* 删除特征弹窗 */}
      {deleteFeature && (
        <DeleteFeatureModal feature={deleteFeature} onClose={()=>setDeleteFeature(null)} onDelete={id=>{
          setFeatures(f=>f.filter(x=>x.id!==id));
          setDeleteFeature(null);
        }} />
      )}
      {/* 只读详情弹窗 */}
      {detailFeature && <FeatureDetailModal feature={detailFeature} onClose={()=>setDetailFeature(null)} />}
    </div>
  );
} 