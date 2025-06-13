import React, { useState } from 'react';
import {
    Modal,
    Card,
    Steps,
    Button,
    Alert,
    Descriptions,
    Table,
    Tag,
    Space,
    Typography,
    message,
} from 'antd';
import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

import { executionApi, type ExecutionRecord } from '@/api/executionApi';
import type { Task } from '@/types/task';

const { Text } = Typography;

interface RetryDiagnosticProps {
    visible: boolean;
    onCancel: () => void;
    task: Task | null;
}

const RetryDiagnostic: React.FC<RetryDiagnosticProps> = ({
    visible,
    onCancel,
    task,
}) => {
    const [loading, setLoading] = useState(false);
    const [executionRecords, setExecutionRecords] = useState<ExecutionRecord[]>([]);

    // 加载执行记录
    const loadExecutionRecords = async () => {
        if (!task) return;

        try {
            setLoading(true);
            const records = await executionApi.getExecutions({ task_id: task.id, limit: 50 });
            setExecutionRecords(Array.isArray(records) ? records : []);
            console.log('📋 加载执行记录:', records);
        } catch (error: any) {
            console.error('❌ 加载执行记录失败:', error);
            message.error(`加载执行记录失败: ${error.message || '未知错误'}`);
            setExecutionRecords([]);
        } finally {
            setLoading(false);
        }
    };

    // 当模态框打开时加载数据
    React.useEffect(() => {
        if (visible && task) {
            loadExecutionRecords();
        }
    }, [visible, task]);

    if (!task) return null;

    // 诊断结果
    const diagnosticResults = {
        taskType: task.task_type === 'retry',
        retryConfig: task.retry_config && task.retry_config.max_attempts > 1,
        hasExecutions: executionRecords.length > 0,
        hasMultipleAttempts: executionRecords.length > 1,
        attemptNumbers: [...new Set(executionRecords.map(r => r.attempt_number))].sort(),
    };

    // 问题诊断
    const issues = [];
    if (!diagnosticResults.taskType) {
        issues.push({
            type: 'error',
            title: '任务类型错误',
            message: `当前任务类型是 "${task.task_type}"，需要设置为 "retry" 才能启用重试功能`,
        });
    }
    if (!diagnosticResults.retryConfig) {
        issues.push({
            type: 'error',
            title: '重试配置错误',
            message: '重试配置无效或最大尝试次数小于等于1',
        });
    }
    if (!diagnosticResults.hasExecutions) {
        issues.push({
            type: 'warning',
            title: '没有执行记录',
            message: '任务尚未执行或执行记录已被清理',
        });
    }
    if (diagnosticResults.hasExecutions && !diagnosticResults.hasMultipleAttempts) {
        issues.push({
            type: 'warning',
            title: '只有一次执行记录',
            message: '任务可能在第一次执行后就满足成功条件而停止，或者配置有误',
        });
    }

    // 执行记录表格列
    const columns: ColumnsType<ExecutionRecord> = [
        {
            title: '尝试次数',
            dataIndex: 'attempt_number',
            key: 'attempt_number',
            width: 100,
            sorter: (a, b) => a.attempt_number - b.attempt_number,
            render: (num: number) => (
                <Tag color="blue">第{num}次</Tag>
            ),
        },
        {
            title: '执行时间',
            dataIndex: 'execution_time',
            key: 'execution_time',
            width: 160,
            render: (time: string) => dayjs(time).format('MM-DD HH:mm:ss'),
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            width: 100,
            render: (status: string) => {
                const config = {
                    success: { color: 'success', icon: <CheckCircleOutlined /> },
                    failed: { color: 'error', icon: <CloseCircleOutlined /> },
                    timeout: { color: 'warning', icon: <ExclamationCircleOutlined /> },
                }[status] || { color: 'default', icon: null };

                return (
                    <Tag color={config.color} icon={config.icon}>
                        {status}
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
            title: '错误信息',
            dataIndex: 'error_message',
            key: 'error_message',
            ellipsis: true,
            render: (error: string) => error || '-',
        },
    ];

    return (
        <Modal
            title={`重试功能诊断 - ${task.name}`}
            open={visible}
            onCancel={onCancel}
            width={1000}
            footer={[
                <Button
                    key="refresh"
                    icon={<ReloadOutlined />}
                    onClick={loadExecutionRecords}
                    loading={loading}
                >
                    刷新数据
                </Button>,
                <Button key="close" onClick={onCancel}>
                    关闭
                </Button>
            ]}
        >
            <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
                {/* 诊断步骤 */}
                <Card title="诊断步骤" style={{ marginBottom: 16 }}>
                    <Steps
                        current={issues.length === 0 ? 2 : (diagnosticResults.taskType ? (diagnosticResults.retryConfig ? 2 : 1) : 0)}
                        status={issues.length === 0 ? 'finish' : 'error'}
                        items={[
                            {
                                title: '任务类型检查',
                                status: diagnosticResults.taskType ? 'finish' : 'error',
                                icon: diagnosticResults.taskType ? <CheckCircleOutlined /> : <CloseCircleOutlined />,
                            },
                            {
                                title: '重试配置检查',
                                status: diagnosticResults.retryConfig ? 'finish' : 'error',
                                icon: diagnosticResults.retryConfig ? <CheckCircleOutlined /> : <CloseCircleOutlined />,
                            },
                            {
                                title: '执行记录检查',
                                status: diagnosticResults.hasMultipleAttempts ? 'finish' : 'error',
                                icon: diagnosticResults.hasMultipleAttempts ? <CheckCircleOutlined /> : <CloseCircleOutlined />,
                            },
                        ]}
                    />
                </Card>

                {/* 问题提示 */}
                {issues.length > 0 && (
                    <Card title="发现的问题" style={{ marginBottom: 16 }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                            {issues.map((issue, index) => (
                                <Alert
                                    key={index}
                                    type={issue.type as any}
                                    message={issue.title}
                                    description={issue.message}
                                    showIcon
                                />
                            ))}
                        </Space>
                    </Card>
                )}

                {/* 任务配置信息 */}
                <Card title="任务配置信息" style={{ marginBottom: 16 }}>
                    <Descriptions column={2} bordered size="small">
                        <Descriptions.Item label="任务类型">
                            <Tag color={task.task_type === 'retry' ? 'success' : 'error'}>
                                {task.task_type}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="任务状态">
                            <Tag color={task.status === 'completed' ? 'success' : 'processing'}>
                                {task.status}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="最大尝试次数">
                            {task.retry_config?.max_attempts || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="重试间隔">
                            {task.retry_config?.interval_seconds || 'N/A'} 秒
                        </Descriptions.Item>
                        <Descriptions.Item label="成功条件">
                            <Text code>{task.retry_config?.success_condition || '未设置'}</Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="停止条件">
                            <Text code>{task.retry_config?.stop_condition || '未设置'}</Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="关键消息">
                            <Text code>{task.retry_config?.key_message || '未设置'}</Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="执行统计">
                            总计: {task.execution_count}, 成功: {task.success_count}, 失败: {task.failure_count}
                        </Descriptions.Item>
                    </Descriptions>
                </Card>

                {/* 执行记录表格 */}
                <Card
                    title={`执行记录 (${executionRecords.length} 条)`}
                    extra={
                        <Text type="secondary">
                            尝试次数范围: {diagnosticResults.attemptNumbers.join(', ') || '无'}
                        </Text>
                    }
                >
                    <Table
                        columns={columns}
                        dataSource={executionRecords}
                        rowKey="id"
                        loading={loading}
                        pagination={{
                            pageSize: 10,
                            showSizeChanger: true,
                            showTotal: (total) => `共 ${total} 条记录`,
                        }}
                        size="small"
                        locale={{
                            emptyText: loading ? '加载中...' : '暂无执行记录'
                        }}
                    />
                </Card>

                {/* 解决建议 */}
                {issues.length > 0 && (
                    <Card title="解决建议" style={{ marginTop: 16 }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                            {!diagnosticResults.taskType && (
                                <Alert
                                    type="info"
                                    message="如何设置重试任务"
                                    description={
                                        <div>
                                            <p>1. 编辑任务，将任务类型改为"重试"</p>
                                            <p>2. 在重试配置中设置最大尝试次数（&gt;1）</p>
                                            <p>3. 根据需要设置重试间隔和成功/停止条件</p>
                                        </div>
                                    }
                                />
                            )}
                            {diagnosticResults.taskType && !diagnosticResults.hasMultipleAttempts && (
                                <Alert
                                    type="info"
                                    message="重试提前停止的可能原因"
                                    description={
                                        <div>
                                            <p>1. 设置了成功条件，第一次请求就满足了条件</p>
                                            <p>2. 设置了关键消息，响应中包含了该消息</p>
                                            <p>3. 请求返回2xx状态码被认为是成功（默认行为）</p>
                                            <p>4. 建议：清空成功条件和关键消息，让任务执行完所有重试次数</p>
                                        </div>
                                    }
                                />
                            )}
                        </Space>
                    </Card>
                )}
            </div>
        </Modal>
    );
};

export default RetryDiagnostic; 