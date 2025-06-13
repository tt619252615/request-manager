import React, { useState, useEffect } from 'react';
import {
    Card,
    Row,
    Col,
    Statistic,
    Timeline,
    Table,
    Button,
    Tag,
    message,
    Spin,
} from 'antd';
import {
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    PlayCircleOutlined,
    ReloadOutlined,
    PauseCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

import { taskApi, type TaskStats } from '../../api/taskApi';
import { requestApi } from '../../api/requestApi';
import { executionApi, type ExecutionStats } from '../../api/executionApi';
import type { Task } from '../../types/task.d.ts';
import type { HttpRequest } from '../../types/request.d.ts';

interface DashboardStats {
    totalRequests: number;
    totalTasks: number;
    runningTasks: number;
    completedToday: number;
    failedToday: number;
    successRate: number;
}

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
        totalRequests: 0,
        totalTasks: 0,
        runningTasks: 0,
        completedToday: 0,
        failedToday: 0,
        successRate: 0,
    });
    const [taskStats, setTaskStats] = useState<TaskStats | null>(null);
    const [executionStats, setExecutionStats] = useState<ExecutionStats | null>(null);
    const [recentTasks, setRecentTasks] = useState<Task[]>([]);
    const [recentRequests, setRecentRequests] = useState<HttpRequest[]>([]);

    // 加载数据
    const loadData = async () => {
        try {
            setLoading(true);

            // 并行获取数据，提高加载效率
            const [taskStatsData, tasksData, requestsData, executionStatsData] = await Promise.allSettled([
                taskApi.getTaskStats(),
                taskApi.getTasks({ limit: 5 }),
                requestApi.getRequests({ limit: 5 }),
                executionApi.getExecutionStats()
            ]);

            // 处理任务统计数据
            if (taskStatsData.status === 'fulfilled' && taskStatsData.value) {
                setTaskStats(taskStatsData.value);
            } else {
                console.warn('获取任务统计失败:', taskStatsData.status === 'rejected' ? taskStatsData.reason : '数据为空');
                // 设置默认值
                setTaskStats({
                    total: 0,
                    running: 0,
                    pending: 0,
                    completed: 0,
                    failed: 0,
                    stopped: 0
                });
            }

            // 处理任务列表数据
            if (tasksData.status === 'fulfilled' && Array.isArray(tasksData.value)) {
                setRecentTasks(tasksData.value);
            } else {
                console.warn('获取任务列表失败:', tasksData.status === 'rejected' ? tasksData.reason : '数据格式异常');
                setRecentTasks([]);
            }

            // 处理请求列表数据
            let requestCount = 0;
            if (requestsData.status === 'fulfilled' && Array.isArray(requestsData.value)) {
                setRecentRequests(requestsData.value);
                requestCount = requestsData.value.length;
            } else {
                console.warn('获取请求列表失败:', requestsData.status === 'rejected' ? requestsData.reason : '数据格式异常');
                setRecentRequests([]);
            }

            // 处理执行统计数据
            if (executionStatsData.status === 'fulfilled' && executionStatsData.value) {
                setExecutionStats(executionStatsData.value);
            } else {
                console.warn('获取执行统计失败:', executionStatsData.status === 'rejected' ? executionStatsData.reason : '数据为空');
                setExecutionStats({
                    total: 0,
                    success: 0,
                    failed: 0,
                    timeout: 0,
                    success_rate: 0
                });
            }

            // 计算成功率，确保taskStats不为null
            const currentTaskStats = taskStats || { completed: 0, failed: 0, total: 0, running: 0, pending: 0, stopped: 0 };
            const totalExecutions = currentTaskStats.completed + currentTaskStats.failed;
            const successRate = totalExecutions > 0 ?
                Math.round((currentTaskStats.completed / totalExecutions) * 100) : 0;

            setDashboardStats({
                totalRequests: requestCount,
                totalTasks: currentTaskStats.total,
                runningTasks: currentTaskStats.running,
                completedToday: currentTaskStats.completed,
                failedToday: currentTaskStats.failed,
                successRate,
            });
        } catch (error) {
            console.error('加载仪表板数据失败:', error);
            message.error('加载数据失败');
            // 设置默认统计数据，避免页面崩溃
            setDashboardStats({
                totalRequests: 0,
                totalTasks: 0,
                runningTasks: 0,
                completedToday: 0,
                failedToday: 0,
                successRate: 0,
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    // 最近活动数据
    const getRecentActivities = () => {
        const activities: Array<{
            time: string;
            content: string;
            type: 'success' | 'info' | 'error' | 'processing';
        }> = [];

        // 添加最近的任务活动
        recentTasks.forEach(task => {
            if (task.last_execution_at) {
                activities.push({
                    time: task.last_execution_at,
                    content: `任务 "${task.name}" 执行${task.status === 'completed' ? '成功' : '失败'}`,
                    type: task.status === 'completed' ? 'success' : 'error',
                });
            }
            activities.push({
                time: task.created_at,
                content: `创建任务 "${task.name}"`,
                type: 'info',
            });
        });

        // 添加最近的请求活动
        recentRequests.forEach(request => {
            activities.push({
                time: request.created_at,
                content: `导入请求 "${request.name}"`,
                type: 'info',
            });
        });

        // 按时间排序并返回最近的10条
        return activities
            .sort((a, b) => dayjs(b.time).valueOf() - dayjs(a.time).valueOf())
            .slice(0, 10);
    };

    // 任务状态映射
    const getTaskStatusTag = (status: string) => {
        const statusMap: Record<string, { color: string; icon: React.ReactNode }> = {
            running: { color: 'processing', icon: <PlayCircleOutlined /> },
            pending: { color: 'default', icon: <PauseCircleOutlined /> },
            completed: { color: 'success', icon: <CheckCircleOutlined /> },
            failed: { color: 'error', icon: <ExclamationCircleOutlined /> },
            stopped: { color: 'warning', icon: <PauseCircleOutlined /> },
        };

        const config = statusMap[status] || { color: 'default', icon: null };
        return (
            <Tag color={config.color} icon={config.icon}>
                {status.toUpperCase()}
            </Tag>
        );
    };

    // 任务表格列
    const taskColumns = [
        {
            title: '任务名称',
            dataIndex: 'name',
            key: 'name',
            ellipsis: true,
            render: (text: string) => (
                <Button
                    type="link"
                    onClick={() => navigate('/tasks')}
                    style={{ padding: 0 }}
                >
                    {text}
                </Button>
            ),
        },
        {
            title: '类型',
            dataIndex: 'task_type',
            key: 'task_type',
            render: (type: string) => (
                <Tag color="blue">{type}</Tag>
            ),
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => getTaskStatusTag(status),
        },
        {
            title: '执行次数',
            dataIndex: 'execution_count',
            key: 'execution_count',
            render: (count: number) => count || 0,
        },
        {
            title: '更新时间',
            dataIndex: 'updated_at',
            key: 'updated_at',
            render: (time: string) => new Date(time).toLocaleString(),
        },
    ];

    // 请求表格列
    const requestColumns = [
        {
            title: '请求名称',
            dataIndex: 'name',
            key: 'name',
            ellipsis: true,
        },
        {
            title: '方法',
            dataIndex: 'method',
            key: 'method',
            render: (method: string) => (
                <Tag color={method === 'GET' ? 'green' : method === 'POST' ? 'blue' : 'orange'}>
                    {method}
                </Tag>
            ),
        },
        {
            title: 'URL',
            dataIndex: 'url',
            key: 'url',
            ellipsis: true,
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (time: string) => new Date(time).toLocaleString(),
        },
    ];

    return (
        <div>
            {/* 页面头部 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1>系统概览</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ color: '#666', fontSize: '14px' }}>
                        状态: {loading ? '加载中...' : `总计 ${dashboardStats.totalTasks} 个任务, ${dashboardStats.totalRequests} 个请求, 成功率 ${dashboardStats.successRate}%`}
                    </span>
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={loadData}
                        loading={loading}
                    >
                        刷新数据
                    </Button>
                </div>
            </div>

            <Spin spinning={loading}>
                {/* 统计卡片 */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="任务总数"
                                value={taskStats?.total || 0}
                                prefix={<PlayCircleOutlined />}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="运行中"
                                value={taskStats?.running || 0}
                                valueStyle={{ color: '#1890ff' }}
                                prefix={<PlayCircleOutlined />}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="已完成"
                                value={taskStats?.completed || 0}
                                valueStyle={{ color: '#52c41a' }}
                                prefix={<CheckCircleOutlined />}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="失败/停止"
                                value={(taskStats?.failed || 0) + (taskStats?.stopped || 0)}
                                valueStyle={{ color: '#ff4d4f' }}
                                prefix={<ExclamationCircleOutlined />}
                            />
                        </Card>
                    </Col>
                </Row>

                {/* 执行统计 */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="总执行次数"
                                value={executionStats?.total || 0}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="成功次数"
                                value={executionStats?.success || 0}
                                valueStyle={{ color: '#52c41a' }}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="失败次数"
                                value={(executionStats?.failed || 0) + (executionStats?.timeout || 0)}
                                valueStyle={{ color: '#ff4d4f' }}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="成功率"
                                value={executionStats?.success_rate || 0}
                                precision={1}
                                suffix="%"
                                valueStyle={{
                                    color: (executionStats?.success_rate || 0) > 90 ? '#52c41a' :
                                        (executionStats?.success_rate || 0) > 70 ? '#faad14' : '#ff4d4f'
                                }}
                            />
                        </Card>
                    </Col>
                </Row>

                {/* 任务状态分布 */}
                {taskStats && (
                    <Row gutter={16} style={{ marginBottom: 24 }}>
                        <Col span={24}>
                            <Card title="任务状态分布">
                                <Row gutter={16}>
                                    <Col span={4}>
                                        <Statistic
                                            title="待运行"
                                            value={taskStats.pending}
                                            valueStyle={{ color: '#722ed1' }}
                                        />
                                    </Col>
                                    <Col span={4}>
                                        <Statistic
                                            title="运行中"
                                            value={taskStats.running}
                                            valueStyle={{ color: '#1890ff' }}
                                        />
                                    </Col>
                                    <Col span={4}>
                                        <Statistic
                                            title="已完成"
                                            value={taskStats.completed}
                                            valueStyle={{ color: '#52c41a' }}
                                        />
                                    </Col>
                                    <Col span={4}>
                                        <Statistic
                                            title="失败"
                                            value={taskStats.failed}
                                            valueStyle={{ color: '#ff4d4f' }}
                                        />
                                    </Col>
                                    <Col span={4}>
                                        <Statistic
                                            title="已停止"
                                            value={taskStats.stopped}
                                            valueStyle={{ color: '#8c8c8c' }}
                                        />
                                    </Col>
                                </Row>
                            </Card>
                        </Col>
                    </Row>
                )}

                <Row gutter={16}>
                    {/* 最近活动 */}
                    <Col span={12}>
                        <Card
                            title="最近活动"
                            style={{ height: '450px' }}
                            extra={
                                <Button
                                    type="link"
                                    size="small"
                                    onClick={() => navigate('/tasks')}
                                >
                                    查看全部
                                </Button>
                            }
                        >
                            <div style={{ height: '350px', overflow: 'auto' }}>
                                <Timeline
                                    items={getRecentActivities().map(activity => ({
                                        color: activity.type === 'success' ? 'green' :
                                            activity.type === 'error' ? 'red' :
                                                activity.type === 'processing' ? 'blue' : 'gray',
                                        children: (
                                            <div>
                                                <p style={{ margin: 0, fontSize: '14px' }}>
                                                    {activity.content}
                                                </p>
                                                <small style={{ color: '#999' }}>
                                                    {dayjs(activity.time).format('MM-DD HH:mm:ss')}
                                                </small>
                                            </div>
                                        )
                                    }))}
                                />
                            </div>
                        </Card>
                    </Col>

                    {/* 最近任务 */}
                    <Col span={12}>
                        <Card
                            title="最近任务"
                            style={{ height: '450px' }}
                            extra={
                                <Button
                                    type="link"
                                    size="small"
                                    onClick={() => navigate('/tasks')}
                                >
                                    查看全部
                                </Button>
                            }
                        >
                            <Table
                                columns={taskColumns}
                                dataSource={recentTasks}
                                rowKey="id"
                                pagination={false}
                                size="small"
                                scroll={{ y: 350 }}
                            />
                        </Card>
                    </Col>
                </Row>

                {/* 最近请求 */}
                <Col span={12}>
                    <Card
                        title="最近请求"
                        style={{ height: '450px' }}
                        extra={
                            <Button
                                type="link"
                                size="small"
                                onClick={() => navigate('/requests')}
                            >
                                查看全部
                            </Button>
                        }
                    >
                        <Table
                            columns={requestColumns}
                            dataSource={recentRequests}
                            rowKey="id"
                            pagination={false}
                            size="small"
                            scroll={{ y: 350 }}
                        />
                    </Card>
                </Col>
            </Spin>
        </div>
    );
};

export default Dashboard; 