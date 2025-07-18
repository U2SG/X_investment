import React, { useState, useEffect } from 'react';

function TagsPage() {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/tags', {
      headers: {
        'Authorization': token ? `Bearer ${token}` : undefined
      }
    })
      .then(res => {
        if (!res.ok) throw new Error('获取标签失败');
        return res.json();
      })
      .then(data => {
        setTags(data);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>加载中...</div>;
  if (error) return <div style={{color: 'red'}}>错误: {error}</div>;

  return (
    <div>
      <h2>标签管理</h2>
      <table className="tags-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>被引用次数</th>
          </tr>
        </thead>
        <tbody>
          {tags.map(tag => (
            <tr key={tag.id}>
              <td>{tag.name}</td>
              <td>{tag.ref_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TagsPage; 