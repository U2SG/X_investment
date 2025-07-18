// 信号编辑弹窗组件
// props:
//   signal: 信号对象
//   onClose: 关闭弹窗回调
//   onSuccess: 操作成功后回调（如刷新列表）

import React, { useState } from 'react';

// SignalEditModal: 信号编辑弹窗
export default function SignalEditModal({ signal, onClose, onSuccess }) {
// ...原内容不变... 