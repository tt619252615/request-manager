import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Button, theme, Breadcrumb } from 'antd';
import {
    DashboardOutlined,
    ApiOutlined,
    ClockCircleOutlined,
    SettingOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    GithubOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content, Footer } = AntLayout;

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const [collapsed, setCollapsed] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    // 菜单项配置
    const menuItems = [
        {
            key: '/dashboard',
            icon: <DashboardOutlined />,
            label: '仪表板',
        },
        {
            key: '/requests',
            icon: <ApiOutlined />,
            label: '请求管理',
        },
        {
            key: '/tasks',
            icon: <ClockCircleOutlined />,
            label: '任务调度',
        },
        {
            key: '/settings',
            icon: <SettingOutlined />,
            label: '系统设置',
        },
    ];

    // 面包屑配置
    const getBreadcrumbItems = () => {
        const pathMap: Record<string, string[]> = {
            '/dashboard': ['仪表板'],
            '/requests': ['请求管理'],
            '/tasks': ['任务调度'],
            '/settings': ['系统设置'],
        };

        const items = pathMap[location.pathname] || ['未知页面'];
        return items.map((item) => ({ title: item }));
    };

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Sider trigger={null} collapsible collapsed={collapsed}>
                <div style={{
                    height: 32,
                    margin: 16,
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: borderRadiusLG,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: collapsed ? '14px' : '16px'
                }}>
                    {collapsed ? 'RM' : 'RequestManager'}
                </div>
                <Menu
                    theme="dark"
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={({ key }) => navigate(key)}
                />
            </Sider>

            <AntLayout>
                <Header style={{
                    padding: 0,
                    background: colorBgContainer,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    paddingRight: 24
                }}>
                    <Button
                        type="text"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setCollapsed(!collapsed)}
                        style={{
                            fontSize: '16px',
                            width: 64,
                            height: 64,
                        }}
                    />

                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <span style={{ color: '#666' }}>RequestManager v0.1.0</span>
                        <Button
                            type="text"
                            icon={<GithubOutlined />}
                            href="https://github.com/your-org/request-manager"
                            target="_blank"
                        />
                    </div>
                </Header>

                <Content style={{ margin: '0 16px' }}>
                    <Breadcrumb
                        style={{ margin: '16px 0' }}
                        items={getBreadcrumbItems()}
                    />

                    <div
                        style={{
                            padding: 24,
                            minHeight: 360,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        {children}
                    </div>
                </Content>

                <Footer style={{ textAlign: 'center' }}>
                    RequestManager ©{new Date().getFullYear()} Created by RequestManager Team
                </Footer>
            </AntLayout>
        </AntLayout>
    );
};

export default Layout; 