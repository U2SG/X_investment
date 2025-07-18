import React, { useState } from 'react';

const QUESTIONS = [
  {
    id: 1,
    text: '1. 您的年龄属于以下哪个区间？',
    options: ['18-30', '31-45', '46-60', '60以上']
  },
  {
    id: 2,
    text: '2. 您的投资经验如何？',
    options: ['无经验', '1-3年', '3-5年', '5年以上']
  },
  {
    id: 3,
    text: '3. 您能承受的最大投资亏损比例？',
    options: ['5%以内', '5%-10%', '10%-20%', '20%以上']
  },
  {
    id: 4,
    text: '4. 您的投资目标更偏向于？',
    options: ['保本', '稳健增值', '平衡', '高风险高收益']
  },
  {
    id: 5,
    text: '5. 遇到市场大幅波动时，您的反应更可能是？',
    options: ['立即止损', '部分减仓', '保持不动', '逢低加仓']
  }
];

function RiskAssessmentPage() {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error' | null
  const [submitError, setSubmitError] = useState(null);

  const handleChange = (qid, value) => {
    setAnswers(a => ({ ...a, [qid]: value }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    setSubmitted(true);
    setSubmitStatus(null);
    setSubmitError(null);
    const token = localStorage.getItem('token');
    fetch('/risk_assessment/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : undefined
      },
      body: JSON.stringify(answers)
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || '提交失败'); });
        return res.json();
      })
      .then(() => {
        setSubmitStatus('success');
      })
      .catch(e => {
        setSubmitStatus('error');
        setSubmitError(e.message);
      });
  };

  return (
    <div>
      <h2>风险测评 / 用户画像</h2>
      <form className="risk-form" onSubmit={handleSubmit} style={{maxWidth: 480}}>
        {QUESTIONS.map(q => (
          <div key={q.id} style={{marginBottom: 16}}>
            <div>{q.text}</div>
            {q.options.map(opt => (
              <label key={opt} style={{marginRight: 16}}>
                <input
                  type="radio"
                  name={`q${q.id}`}
                  value={opt}
                  checked={answers[q.id] === opt}
                  onChange={() => handleChange(q.id, opt)}
                  required
                />
                {opt}
              </label>
            ))}
          </div>
        ))}
        <button type="submit">提交</button>
      </form>
      {submitted && (
        <div style={{marginTop: 24}}>
          {submitStatus === 'success' && <div style={{color: 'green'}}>提交成功！</div>}
          {submitStatus === 'error' && <div style={{color: 'red'}}>提交失败: {submitError}</div>}
          <h3>您的答案：</h3>
          <ul>
            {QUESTIONS.map(q => (
              <li key={q.id}>{q.text} <b>{answers[q.id]}</b></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RiskAssessmentPage; 