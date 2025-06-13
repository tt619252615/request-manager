import React, { useState, useEffect, useCallback } from 'react';
import {
    Button,
    Table,
    Space,
    Card,
    Tag,
    Badge,
    Dropdown,
    Modal,
    message,
    Input,
    Select,
    Tooltip,
    Row,
    Col,
    Statistic,
    App,
    Descriptions,
    Typography,
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    PlayCircleOutlined,
    PauseCircleOutlined,
    ReloadOutlined,
    ImportOutlined,
    CopyOutlined,
    HistoryOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    ClockCircleOutlined,
    ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { BadgeProps, MenuProps } from 'antd';
import dayjs from 'dayjs';

import { taskApi, type TaskStats } from '@/api/taskApi';
import { executionApi, type ExecutionRecord } from '@/api/executionApi';
import type { Task, TaskStatus, TaskType } from '@/types/task';
import TaskForm from './components/TaskForm';
import FiddlerImportModal from './components/FiddlerImportModal';
import RetryDiagnostic from './components/RetryDiagnostic';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

const Tasks: React.FC = () => {
    const { modal, message: messageApi } = App.useApp();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(false);
    const [taskFormVisible, setTaskFormVisible] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | null>(null);
    const [stats, setStats] = useState<TaskStats | null>(null);

    // 执行记录相关状态
    const [executionModalVisible, setExecutionModalVisible] = useState(false);
    const [selectedTaskForExecution, setSelectedTaskForExecution] = useState<Task | null>(null);
    const [executionRecords, setExecutionRecords] = useState<ExecutionRecord[]>([]);
    const [executionLoading, setExecutionLoading] = useState(false);

    // 搜索和过滤
    const [searchText, setSearchText] = useState('');
    const [statusFilter, setStatusFilter] = useState<TaskStatus | undefined>();
    const [typeFilter, setTypeFilter] = useState<TaskType | undefined>();

    // 重试诊断相关状态
    const [retryDiagnosticVisible, setRetryDiagnosticVisible] = useState(false);
    const [selectedTaskForDiagnostic, setSelectedTaskForDiagnostic] = useState<Task | null>(null);

    // 加载数据
    const loadTasks = useCallback(async () => {
        try {
            setLoading(true);
            const params = {
                search: searchText || undefined,
                status: statusFilter,
                task_type: typeFilter,
            };
            const data = await taskApi.getTasks(params);
            // 确保数据是数组类型
            if (Array.isArray(data)) {
                setTasks(data);
            } else {
                console.warn('任务列表数据格式异常:', data);
                setTasks([]);
            }
        } catch (error) {
            console.error('加载任务列表失败:', error);
            messageApi.error('加载任务列表失败');
            setTasks([]);
        } finally {
            setLoading(false);
        }
    }, [searchText, statusFilter, typeFilter, messageApi]);

    // 加载统计信息
    const loadStats = async () => {
        try {
            const data = await taskApi.getTaskStats();
            if (data && typeof data === 'object') {
                setStats(data);
            } else {
                console.warn('任务统计数据格式异常:', data);
                // 设置默认统计数据
                setStats({
                    total: 0,
                    running: 0,
                    pending: 0,
                    completed: 0,
                    failed: 0,
                    stopped: 0,
                    scheduler_running_count: 0
                });
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
            // 设置默认统计数据
            setStats({
                total: 0,
                running: 0,
                pending: 0,
                completed: 0,
                failed: 0,
                stopped: 0,
                scheduler_running_count: 0
            });
        }
    };

    useEffect(() => {
        loadTasks();
        loadStats();
    }, [loadTasks]);

    // 启动任务
    const handleStartTask = async (task: Task) => {
        try {
            console.log('🚀 正在启动任务:', task.id, task.name);
            const result = await taskApi.startTask(task.id);
            console.log('🚀 启动任务返回结果:', result);

            messageApi.success(`任务 "${task.name}" 启动成功`);

            // 重新加载数据
            await Promise.all([loadTasks(), loadStats()]);
        } catch (error: any) {
            console.error('❌ 启动任务失败:', error);
            messageApi.error(`启动任务失败: ${error.message || '未知错误'}`);
        }
    };

    // 停止任务
    const handleStopTask = async (task: Task) => {
        try {
            console.log('⏹️ 正在停止任务:', task.id, task.name);
            const result = await taskApi.stopTask(task.id);
            console.log('⏹️ 停止任务返回结果:', result);

            messageApi.success(`任务 "${task.name}" 停止成功`);

            // 重新加载数据
            await Promise.all([loadTasks(), loadStats()]);
        } catch (error: any) {
            console.error('❌ 停止任务失败:', error);
            messageApi.error(`停止任务失败: ${error.message || '未知错误'}`);
        }
    };

    // 删除任务
    const handleDeleteTask = async (task: Task) => {
        try {
            console.log('🗑️ 正在删除任务:', task.id, task.name);
            const result = await taskApi.deleteTask(task.id);
            console.log('🗑️ 删除任务返回结果:', result);

            messageApi.success(`任务 "${task.name}" 删除成功`);

            // 重新加载数据
            await Promise.all([loadTasks(), loadStats()]);
        } catch (error: any) {
            console.error('❌ 删除任务失败:', error);
            messageApi.error(`删除任务失败: ${error.message || '未知错误'}`);
        }
    };

    // 复制任务
    const handleDuplicateTask = async (task: Task) => {
        modal.confirm({
            title: '复制任务',
            content: (
                <div>
                    <p>将复制任务: {task.name}</p>
                    <Input
                        placeholder="请输入新任务名称"
                        id="new-task-name"
                        defaultValue={`${task.name}_副本`}
                    />
                </div>
            ),
            onOk: async () => {
                const input = document.getElementById('new-task-name') as HTMLInputElement;
                const newName = input?.value.trim();
                if (!newName) {
                    messageApi.error('请输入新任务名称');
                    return;
                }
                try {
                    await taskApi.duplicateTask(task.id, newName);
                    messageApi.success('任务复制成功');
                    loadTasks();
                } catch (error: any) {
                    messageApi.error(error.message || '复制任务失败');
                }
            },
        });
    };

    // 编辑任务
    const handleEditTask = (task: Task) => {
        setEditingTask(task);
        setTaskFormVisible(true);
    };

    // 任务表单成功回调
    const handleTaskFormSuccess = () => {
        setTaskFormVisible(false);
        setEditingTask(null);
        loadTasks();
        loadStats();
    };

    // 导入成功回调
    const handleImportSuccess = () => {
        setImportModalVisible(false);
        messageApi.success('请求导入成功，现在可以基于此请求创建任务');
    };

    // 查看执行记录
    const handleViewExecutions = async (task: Task) => {
        try {
            setSelectedTaskForExecution(task);
            setExecutionModalVisible(true);
            setExecutionLoading(true);

            console.log('🔍 正在加载任务执行记录:', task.id);
            const records = await executionApi.getExecutions({ task_id: task.id, limit: 50 });
            console.log('📋 执行记录数据:', records);

            setExecutionRecords(Array.isArray(records) ? records : []);
        } catch (error: any) {
            console.error('❌ 加载执行记录失败:', error);
            messageApi.error(`加载执行记录失败: ${error.message || '未知错误'}`);
            setExecutionRecords([]);
        } finally {
            setExecutionLoading(false);
        }
    };

    // 重试诊断
    const handleRetryDiagnostic = (task: Task) => {
        console.log('🔧 打开重试诊断:', task.id);
        setSelectedTaskForDiagnostic(task);
        setRetryDiagnosticVisible(true);
    };

    // 表格列定义
    const columns: ColumnsType<Task> = [
        {
            title: '任务名称',
            dataIndex: 'name',
            key: 'name',
            width: 200,
            ellipsis: true,
            render: (text: string, record: Task) => (
                <Tooltip title={record.description || text}>
                    <Button type="link" onClick={() => handleEditTask(record)}>
                        {text}
                    </Button>
                </Tooltip>
            ),
        },
        {
            title: '关联请求',
            dataIndex: 'request_id',
            key: 'request_id',
            width: 120,
            render: (requestId: number) => `请求 #${requestId}`,
        },
        {
            title: '任务类型',
            dataIndex: 'task_type',
            key: 'task_type',
            width: 100,
            render: (type: TaskType) => {
                const typeMap = {
                    single: { color: 'blue', text: '单次' },
                    scheduled: { color: 'green', text: '定时' },
                    retry: { color: 'orange', text: '重试' },
                };
                const config = typeMap[type] || { color: 'default', text: type };
                return <Tag color={config.color}>{config.text}</Tag>;
            },
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            width: 100,
            render: (status: TaskStatus) => {
                const statusMap: Record<TaskStatus, { color: BadgeProps['status']; text: string }> = {
                    pending: { color: 'default', text: '待运行' },
                    running: { color: 'processing', text: '运行中' },
                    stopped: { color: 'error', text: '已停止' },
                    completed: { color: 'success', text: '已完成' },
                    failed: { color: 'error', text: '失败' },
                };
                const config = statusMap[status];
                return <Badge status={config.color} text={config.text} />;
            },
        },
        {
            title: '执行统计',
            key: 'execution_stats',
            width: 120,
            render: (_, record: Task) => (
                <div>
                    <div>总计: {record.execution_count}</div>
                    <div>成功: <span style={{ color: '#52c41a' }}>{record.success_count}</span></div>
                    <div>失败: <span style={{ color: '#ff4d4f' }}>{record.failure_count}</span></div>
                </div>
            ),
        },
        {
            title: '下次执行',
            dataIndex: 'next_execution_at',
            key: 'next_execution_at',
            width: 150,
            render: (time: string) =>
                time ? dayjs(time).format('MM-DD HH:mm:ss') : '-',
        },
        {
            title: '最后执行',
            dataIndex: 'last_execution_at',
            key: 'last_execution_at',
            width: 150,
            render: (time: string) =>
                time ? dayjs(time).format('MM-DD HH:mm:ss') : '-',
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 150,
            render: (time: string) => dayjs(time).format('MM-DD HH:mm:ss'),
        },
        {
            title: '操作',
            key: 'action',
            width: 200,
            fixed: 'right',
            render: (_, record: Task) => {
                const menuItems: MenuProps['items'] = [
                    {
                        key: 'view_executions',
                        icon: <HistoryOutlined />,
                        label: '执行记录',
                    },
                    {
                        key: 'retry_diagnostic',
                        icon: <ExclamationCircleOutlined />,
                        label: '重试诊断',
                    },
                    {
                        type: 'divider',
                    },
                    {
                        key: 'edit',
                        icon: <EditOutlined />,
                        label: '编辑',
                    },
                    {
                        key: 'duplicate',
                        icon: <CopyOutlined />,
                        label: '复制',
                    },
                    {
                        type: 'divider',
                    },
                    {
                        key: 'delete',
                        icon: <DeleteOutlined />,
                        label: '删除',
                        danger: true,
                    },
                ];

                const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
                    console.log(`🎯 菜单点击: ${key}, 任务ID: ${record.id}`);

                    switch (key) {
                        case 'view_executions':
                            handleViewExecutions(record);
                            break;
                        case 'retry_diagnostic':
                            handleRetryDiagnostic(record);
                            break;
                        case 'edit':
                            handleEditTask(record);
                            break;
                        case 'duplicate':
                            handleDuplicateTask(record);
                            break;
                        case 'delete':
                            modal.confirm({
                                title: '确认删除',
                                content: `确定要删除任务 "${record.name}" 吗？此操作不可撤销。`,
                                okType: 'danger',
                                okText: '删除',
                                cancelText: '取消',
                                onOk: async () => {
                                    console.log(`🗑️ 确认删除任务: ${record.id}`);
                                    await handleDeleteTask(record);
                                },
                            });
                            break;
                        default:
                            console.warn('未知的菜单操作:', key);
                    }
                };

                return (
                    <Space size="small">
                        {record.status === 'running' ? (
                            <Button
                                type="primary"
                                danger
                                size="small"
                                icon={<PauseCircleOutlined />}
                                onClick={() => {
                                    console.log(`⏹️ 停止任务: ${record.id}`);
                                    handleStopTask(record);
                                }}
                            >
                                停止
                            </Button>
                        ) : (
                            <Button
                                type="primary"
                                size="small"
                                icon={<PlayCircleOutlined />}
                                onClick={() => {
                                    console.log(`🚀 启动任务: ${record.id}`);
                                    handleStartTask(record);
                                }}
                            >
                                启动
                            </Button>
                        )}
                        <Dropdown
                            menu={{
                                items: menuItems,
                                onClick: handleMenuClick
                            }}
                            placement="bottomRight"
                            trigger={['click']}
                        >
                            <Button size="small">更多</Button>
                        </Dropdown>
                    </Space>
                );
            },
        },
    ];

    return (
        <div>
            {/* 统计卡片 */}
            {stats && (
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={4}>
                        <Card>
                            <Statistic title="总任务数" value={stats.total} />
                        </Card>
                    </Col>
                    <Col span={4}>
                        <Card>
                            <Statistic
                                title="运行中"
                                value={stats.running}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Card>
                    </Col>
                    <Col span={4}>
                        <Card>
                            <Statistic
                                title="待运行"
                                value={stats.pending}
                                valueStyle={{ color: '#722ed1' }}
                            />
                        </Card>
                    </Col>
                    <Col span={4}>
                        <Card>
                            <Statistic
                                title="已完成"
                                value={stats.completed}
                                valueStyle={{ color: '#52c41a' }}
                            />
                        </Card>
                    </Col>
                    <Col span={4}>
                        <Card>
                            <Statistic
                                title="失败"
                                value={stats.failed}
                                valueStyle={{ color: '#ff4d4f' }}
                            />
                        </Card>
                    </Col>
                    <Col span={4}>
                        <Card>
                            <Statistic
                                title="已停止"
                                value={stats.stopped}
                                valueStyle={{ color: '#8c8c8c' }}
                            />
                        </Card>
                    </Col>
                </Row>
            )}

            {/* 页面头部 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h1>任务调度</h1>
                <Space>
                    <Button
                        icon={<ImportOutlined />}
                        onClick={() => setImportModalVisible(true)}
                    >
                        导入Fiddler
                    </Button>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => {
                            setEditingTask(null);
                            setTaskFormVisible(true);
                        }}
                    >
                        新建任务
                    </Button>
                </Space>
            </div>

            {/* 搜索和过滤 */}
            <Card style={{ marginBottom: 16 }}>
                <Space wrap>
                    <Search
                        placeholder="搜索任务名称或描述"
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        onSearch={loadTasks}
                        style={{ width: 300 }}
                        allowClear
                    />
                    <Select
                        placeholder="状态过滤"
                        value={statusFilter}
                        onChange={setStatusFilter}
                        style={{ width: 120 }}
                        allowClear
                    >
                        <Option value="pending">待运行</Option>
                        <Option value="running">运行中</Option>
                        <Option value="stopped">已停止</Option>
                        <Option value="completed">已完成</Option>
                        <Option value="failed">失败</Option>
                    </Select>
                    <Select
                        placeholder="类型过滤"
                        value={typeFilter}
                        onChange={setTypeFilter}
                        style={{ width: 120 }}
                        allowClear
                    >
                        <Option value="single">单次执行</Option>
                        <Option value="scheduled">定时任务</Option>
                        <Option value="retry">循环重试</Option>
                    </Select>
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={() => {
                            loadTasks();
                            loadStats();
                        }}
                    >
                        刷新
                    </Button>
                </Space>
            </Card>

            {/* 任务表格 */}
            <Card>
                <Table
                    columns={columns}
                    dataSource={tasks}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1400 }}
                    pagination={{
                        total: tasks.length,
                        pageSize: 10,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                />
            </Card>

            {/* 任务表单模态框 */}
            <TaskForm
                visible={taskFormVisible}
                onCancel={() => {
                    setTaskFormVisible(false);
                    setEditingTask(null);
                }}
                onSuccess={handleTaskFormSuccess}
                editingTask={editingTask}
            />

            {/* Fiddler导入模态框 */}
            <FiddlerImportModal
                visible={importModalVisible}
                onCancel={() => setImportModalVisible(false)}
                onSuccess={handleImportSuccess}
            />

            {/* 执行记录查看模态框 */}
            <Modal
                title={`执行记录 - ${selectedTaskForExecution?.name}`}
                open={executionModalVisible}
                onCancel={() => {
                    setExecutionModalVisible(false);
                    setSelectedTaskForExecution(null);
                    setExecutionRecords([]);
                }}
                width={1200}
                footer={[
                    <Button
                        key="refresh"
                        icon={<ReloadOutlined />}
                        onClick={() => selectedTaskForExecution && handleViewExecutions(selectedTaskForExecution)}
                    >
                        刷新
                    </Button>,
                    <Button key="close" onClick={() => setExecutionModalVisible(false)}>
                        关闭
                    </Button>
                ]}
            >
                <Table
                    columns={[
                        {
                            title: '执行时间',
                            dataIndex: 'execution_time',
                            key: 'execution_time',
                            width: 160,
                            render: (time: string) => dayjs(time).format('MM-DD HH:mm:ss'),
                            sorter: (a, b) => dayjs(a.execution_time).unix() - dayjs(b.execution_time).unix(),
                            defaultSortOrder: 'descend',
                        },
                        {
                            title: '状态',
                            dataIndex: 'status',
                            key: 'status',
                            width: 100,
                            render: (status: string) => {
                                const statusConfig = {
                                    success: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },
                                    failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
                                    timeout: { color: 'warning', icon: <ClockCircleOutlined />, text: '超时' },
                                };
                                const config = statusConfig[status as keyof typeof statusConfig] ||
                                    { color: 'default', icon: null, text: status };

                                return (
                                    <Tag color={config.color} icon={config.icon}>
                                        {config.text}
                                    </Tag>
                                );
                            },
                        },
                        {
                            title: '状态码',
                            dataIndex: 'response_code',
                            key: 'response_code',
                            width: 80,
                            render: (code: number) => (
                                <Tag color={code >= 200 && code < 300 ? 'success' : 'error'}>
                                    {code || 'N/A'}
                                </Tag>
                            ),
                        },
                        {
                            title: '响应时间',
                            dataIndex: 'response_time',
                            key: 'response_time',
                            width: 100,
                            render: (time: number) => time ? `${time.toFixed(2)}ms` : 'N/A',
                        },
                        {
                            title: '尝试次数',
                            dataIndex: 'attempt_number',
                            key: 'attempt_number',
                            width: 80,
                            render: (num: number) => `第${num}次`,
                        },
                        {
                            title: '代理',
                            dataIndex: 'proxy_used',
                            key: 'proxy_used',
                            width: 120,
                            render: (proxy: string) => proxy ? <Text code>{proxy}</Text> : '本地IP',
                        },
                        {
                            title: '错误信息',
                            dataIndex: 'error_message',
                            key: 'error_message',
                            ellipsis: true,
                            render: (error: string) => error || '-',
                        },
                        {
                            title: '操作',
                            key: 'action',
                            width: 100,
                            render: (_, record: ExecutionRecord) => (
                                <Button
                                    type="link"
                                    size="small"
                                    onClick={() => {
                                        modal.info({
                                            title: '执行详情',
                                            width: 800,
                                            content: (
                                                <div>
                                                    <Descriptions column={1} bordered size="small">
                                                        <Descriptions.Item label="执行时间">
                                                            {dayjs(record.execution_time).format('YYYY-MM-DD HH:mm:ss')}
                                                        </Descriptions.Item>
                                                        <Descriptions.Item label="状态">
                                                            {record.status}
                                                        </Descriptions.Item>
                                                        <Descriptions.Item label="HTTP状态码">
                                                            {record.response_code || 'N/A'}
                                                        </Descriptions.Item>
                                                        <Descriptions.Item label="响应时间">
                                                            {record.response_time ? `${record.response_time.toFixed(2)}ms` : 'N/A'}
                                                        </Descriptions.Item>
                                                        <Descriptions.Item label="使用代理">
                                                            {record.proxy_used || '本地IP'}
                                                        </Descriptions.Item>
                                                        <Descriptions.Item label="线程ID">
                                                            {record.thread_id || 'N/A'}
                                                        </Descriptions.Item>
                                                        {record.error_message && (
                                                            <Descriptions.Item label="错误信息">
                                                                <Text type="danger">{record.error_message}</Text>
                                                            </Descriptions.Item>
                                                        )}
                                                        {record.response_body && (
                                                            <Descriptions.Item label="响应体">
                                                                <div style={{
                                                                    maxHeight: '400px',
                                                                    overflow: 'auto',
                                                                    border: '1px solid #d9d9d9',
                                                                    borderRadius: '6px',
                                                                    padding: '12px',
                                                                    backgroundColor: '#fafafa',
                                                                    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
                                                                    fontSize: '12px',
                                                                    lineHeight: '1.5',
                                                                    whiteSpace: 'pre-wrap',
                                                                    wordBreak: 'break-all',
                                                                    width: '100%'
                                                                }}>
                                                                    {record.response_body}
                                                                </div>
                                                                <div style={{ marginTop: '8px', textAlign: 'right' }}>
                                                                    <Button
                                                                        size="small"
                                                                        onClick={() => {
                                                                            navigator.clipboard.writeText(record.response_body || '');
                                                                            message.success('响应体已复制到剪贴板');
                                                                        }}
                                                                    >
                                                                        复制响应体
                                                                    </Button>
                                                                </div>
                                                            </Descriptions.Item>
                                                        )}
                                                    </Descriptions>
                                                </div>
                                            ),
                                        });
                                    }}
                                >
                                    详情
                                </Button>
                            ),
                        },
                    ]}
                    dataSource={executionRecords}
                    rowKey="id"
                    loading={executionLoading}
                    pagination={{
                        pageSize: 10,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                    size="small"
                    locale={{
                        emptyText: executionLoading ? '加载中...' : '暂无执行记录'
                    }}
                />
            </Modal>

            {/* 重试诊断模态框 */}
            <RetryDiagnostic
                visible={retryDiagnosticVisible}
                onCancel={() => {
                    setRetryDiagnosticVisible(false);
                    setSelectedTaskForDiagnostic(null);
                }}
                task={selectedTaskForDiagnostic}
            />
        </div>
    );
};

export default Tasks; 