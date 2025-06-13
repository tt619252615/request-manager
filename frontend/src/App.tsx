import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

// 配置dayjs中文
dayjs.locale('zh-cn');

// 引入页面组件（暂时创建占位符）
const Dashboard = React.lazy(() => import('@/pages/Dashboard'));
const Requests = React.lazy(() => import('@/pages/Requests'));
const Tasks = React.lazy(() => import('@/pages/Tasks'));
const Settings = React.lazy(() => import('@/pages/Settings'));

// 布局组件
import Layout from '@/components/common/Layout';

function AppContent() {
  return (
      <BrowserRouter>
        <Layout>
          <React.Suspense fallback={<div style={{ padding: '20px', textAlign: 'center' }}>加载中...</div>}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/requests" element={<Requests />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </React.Suspense>
        </Layout>
      </BrowserRouter>
  );
}

function AppRoot() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <App>
        <AppContent />
      </App>
    </ConfigProvider>
  );
}

export default AppRoot;
