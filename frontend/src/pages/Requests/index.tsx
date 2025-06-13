import React, { useState, useEffect, useCallback } from 'react';
import {
    Button,
    Table,
    Space,
    Card,
    Tag,
    Modal,
    Input,
    Select,
    Tooltip,
    Descriptions,
    Typography,
    App,
} from 'antd';
import {
    DeleteOutlined,
    PlayCircleOutlined,
    ReloadOutlined,
    ImportOutlined,
    EyeOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

import { requestApi } from '@/api/requestApi';
import type { HttpRequest } from '@/types/request';
import FiddlerImportModal from '../Tasks/components/FiddlerImportModal';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

const Requests: React.FC = () => {
    const { modal, message: messageApi } = App.useApp();
    const [requests, setRequests] = useState<HttpRequest[]>([]);
    const [loading, setLoading] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [detailModalVisible, setDetailModalVisible] = useState(false);
    const [selectedRequest, setSelectedRequest] = useState<HttpRequest | null>(null);

    // 搜索和过滤
    const [searchText, setSearchText] = useState('');
    const [methodFilter, setMethodFilter] = useState<string | undefined>();

    // 加载数据
    const loadRequests = useCallback(async () => {
        try {
            setLoading(true);
            const params = {
                search: searchText || undefined,
                method: methodFilter,
            };
            console.log('🔍 正在加载请求列表，参数:', params);
            const data = await requestApi.getRequests(params);
            console.log('📦 API返回的原始数据:', data);
            console.log('📋 数据类型:', typeof data, '是否为数组:', Array.isArray(data));

            // 确保数据是数组类型
            if (Array.isArray(data)) {
                console.log('✅ 数据格式正确，设置requests，数据条数:', data.length);
                setRequests(data);
            } else {
                console.warn('⚠️ 请求列表数据格式异常:', data);
                setRequests([]);
            }
        } catch (error) {
            console.error('❌ 加载请求列表失败:', error);
            messageApi.error('加载请求列表失败');
            setRequests([]);
        } finally {
            setLoading(false);
        }
    }, [searchText, methodFilter, messageApi]);

    useEffect(() => {
        loadRequests();
    }, [loadRequests]);

    // 测试请求
    const handleTestRequest = async (request: HttpRequest) => {
        try {
            console.log('🧪 开始测试请求:', request.id);

            // 显示加载消息，会自动销毁
            const hide = messageApi.loading('正在测试请求...', 0);

            const result = await requestApi.testRequest(request.id);
            hide(); // 手动关闭loading消息

            console.log('🧪 测试结果原始数据:', result);

            // 处理测试结果 - 后端返回的数据结构
            const responseData = result || {};
            const statusCode = responseData.status_code || 'N/A';
            const responseTime = responseData.response_time || 'N/A';
            const responseBody = responseData.response_body || responseData.response || '';
            const responseHeaders = responseData.response_headers || responseData.headers || {};
            const errorMessage = responseData.error_message || responseData.error || '';
            const success = responseData.success !== undefined ? responseData.success :
                (statusCode !== 'N/A' && statusCode >= 200 && statusCode < 400 && !errorMessage);

            console.log('🧪 处理后的测试结果:', {
                statusCode,
                responseTime,
                success,
                hasError: !!errorMessage
            });

            // 使用 App.useApp() 的 modal
            modal.info({
                title: `测试结果 - ${request.name}`,
                width: 800,
                icon: success ?
                    <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                    <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
                content: (
                    <div style={{ maxHeight: '60vh', overflow: 'auto' }}>
                        <div style={{ marginBottom: 16 }}>
                            <p><strong>执行状态:</strong>
                                <span style={{
                                    color: success ? '#52c41a' : '#ff4d4f',
                                    marginLeft: 8
                                }}>
                                    {success ? '成功' : '失败'}
                                </span>
                            </p>
                            <p><strong>状态码:</strong> {statusCode}</p>
                            <p><strong>响应时间:</strong> {responseTime}ms</p>
                            {errorMessage && (
                                <p><strong>错误信息:</strong>
                                    <span style={{ color: '#ff4d4f' }}>{errorMessage}</span>
                                </p>
                            )}
                        </div>

                        {responseHeaders && Object.keys(responseHeaders).length > 0 && (
                            <div style={{ marginBottom: 16 }}>
                                <p><strong>响应头:</strong></p>
                                <Paragraph
                                    code
                                    copyable
                                    style={{
                                        maxHeight: 150,
                                        overflow: 'auto',
                                        background: '#f6f8fa',
                                        padding: 8
                                    }}
                                >
                                    {JSON.stringify(responseHeaders, null, 2)}
                                </Paragraph>
                            </div>
                        )}

                        <div>
                            <p><strong>响应体:</strong></p>
                            <Paragraph
                                code
                                copyable
                                ellipsis={{ rows: 15, expandable: true }}
                                style={{
                                    background: '#f6f8fa',
                                    padding: 8,
                                    fontSize: '12px',
                                    fontFamily: 'monospace'
                                }}
                            >
                                {responseBody ?
                                    (typeof responseBody === 'string' ?
                                        responseBody :
                                        JSON.stringify(responseBody, null, 2)
                                    ) :
                                    '(无响应体)'
                                }
                            </Paragraph>
                        </div>
                    </div>
                ),
            });
        } catch (error: any) {
            console.error('❌ 测试请求失败:', error);

            // 显示详细的错误信息
            modal.error({
                title: `测试失败 - ${request.name}`,
                content: (
                    <div>
                        <p><strong>错误信息:</strong> {error.message || '未知错误'}</p>
                        <p><strong>请求ID:</strong> {request.id}</p>
                        <p><strong>请求URL:</strong> {request.url}</p>
                    </div>
                )
            });
        }
    };

    // 删除请求
    const handleDeleteRequest = async (request: HttpRequest) => {
        try {
            console.log('🗑️ 正在删除请求:', request.id, request.name);
            const result = await requestApi.deleteRequest(request.id);
            console.log('🗑️ 删除请求返回结果:', result);

            messageApi.success(`请求 "${request.name}" 删除成功`);

            // 重新加载数据
            await loadRequests();
        } catch (error: any) {
            console.error('❌ 删除请求失败:', error);
            messageApi.error(`删除请求失败: ${error.message || '未知错误'}`);
        }
    };

    // 查看详情
    const handleViewDetail = (request: HttpRequest) => {
        setSelectedRequest(request);
        setDetailModalVisible(true);
    };

    // 导入成功回调
    const handleImportSuccess = () => {
        setImportModalVisible(false);
        loadRequests();
    };

    // 表格列定义
    const columns: ColumnsType<HttpRequest> = [
        {
            title: '请求名称',
            dataIndex: 'name',
            key: 'name',
            width: 200,
            ellipsis: true,
            render: (text: string, record: HttpRequest) => (
                <Tooltip title={record.description || text}>
                    <Button type="link" onClick={() => handleViewDetail(record)}>
                        {text}
                    </Button>
                </Tooltip>
            ),
        },
        {
            title: '方法',
            dataIndex: 'method',
            key: 'method',
            width: 80,
            render: (method: string) => {
                const colors = {
                    GET: 'blue',
                    POST: 'green',
                    PUT: 'orange',
                    DELETE: 'red',
                    PATCH: 'purple',
                };
                return <Tag color={colors[method as keyof typeof colors] || 'default'}>{method}</Tag>;
            },
        },
        {
            title: 'URL',
            dataIndex: 'url',
            key: 'url',
            ellipsis: true,
            render: (url: string) => (
                <Tooltip title={url}>
                    <Text code>{url}</Text>
                </Tooltip>
            ),
        },
        {
            title: '描述',
            dataIndex: 'description',
            key: 'description',
            width: 200,
            ellipsis: true,
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
            render: (_, record: HttpRequest) => (
                <Space size="small">
                    <Button
                        type="primary"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleTestRequest(record)}
                    >
                        测试
                    </Button>
                    <Button
                        size="small"
                        icon={<EyeOutlined />}
                        onClick={() => handleViewDetail(record)}
                    >
                        详情
                    </Button>
                    <Button
                        type="primary"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => {
                            modal.confirm({
                                title: '确认删除',
                                content: `确定要删除请求 "${record.name}" 吗？`,
                                okType: 'danger',
                                onOk: () => handleDeleteRequest(record),
                            });
                        }}
                    >
                        删除
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <div>
            {/* 页面头部 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h1>HTTP请求管理</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ color: '#666', fontSize: '14px' }}>
                        数据状态: {loading ? '加载中...' : `共${requests.length}条记录`}
                    </span>
                    <Button
                        type="primary"
                        icon={<ImportOutlined />}
                        onClick={() => setImportModalVisible(true)}
                    >
                        导入Fiddler请求
                    </Button>
                </div>
            </div>

            {/* 搜索和过滤 */}
            <Card style={{ marginBottom: 16 }}>
                <Space wrap>
                    <Search
                        placeholder="搜索请求名称、URL或描述"
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        onSearch={loadRequests}
                        style={{ width: 350 }}
                        allowClear
                    />
                    <Select
                        placeholder="方法过滤"
                        value={methodFilter}
                        onChange={setMethodFilter}
                        style={{ width: 120 }}
                        allowClear
                    >
                        <Option value="GET">GET</Option>
                        <Option value="POST">POST</Option>
                        <Option value="PUT">PUT</Option>
                        <Option value="DELETE">DELETE</Option>
                        <Option value="PATCH">PATCH</Option>
                    </Select>
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={loadRequests}
                    >
                        刷新
                    </Button>
                    <Button
                        type="dashed"
                        onClick={() => {
                            console.log('🐛 当前requests状态:', requests);
                            console.log('🐛 当前loading状态:', loading);
                        }}
                    >
                        调试信息
                    </Button>
                </Space>
            </Card>

            {/* 请求表格 */}
            <Card>
                <Table
                    columns={columns}
                    dataSource={requests}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1000 }}
                    pagination={{
                        total: requests.length,
                        pageSize: 10,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                    locale={{
                        emptyText: loading ? '数据加载中...' : `暂无数据 (状态: ${requests.length} 条记录)`
                    }}
                />
            </Card>

            {/* Fiddler导入模态框 */}
            <FiddlerImportModal
                visible={importModalVisible}
                onCancel={() => setImportModalVisible(false)}
                onSuccess={handleImportSuccess}
            />

            {/* 请求详情模态框 */}
            <Modal
                title={`请求详情 - ${selectedRequest?.name}`}
                open={detailModalVisible}
                onCancel={() => setDetailModalVisible(false)}
                width={800}
                footer={[
                    <Button key="close" onClick={() => setDetailModalVisible(false)}>
                        关闭
                    </Button>,
                    <Button
                        key="test"
                        type="primary"
                        icon={<PlayCircleOutlined />}
                        onClick={() => {
                            if (selectedRequest) {
                                handleTestRequest(selectedRequest);
                            }
                        }}
                    >
                        测试请求
                    </Button>,
                ]}
            >
                {selectedRequest && (
                    <Descriptions column={1} bordered>
                        <Descriptions.Item label="请求名称">
                            {selectedRequest.name}
                        </Descriptions.Item>
                        <Descriptions.Item label="描述">
                            {selectedRequest.description || '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="方法">
                            <Tag color={
                                selectedRequest.method === 'GET' ? 'blue' :
                                    selectedRequest.method === 'POST' ? 'green' :
                                        selectedRequest.method === 'PUT' ? 'orange' :
                                            selectedRequest.method === 'DELETE' ? 'red' : 'default'
                            }>
                                {selectedRequest.method}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="URL">
                            <Text code copyable>
                                {selectedRequest.url}
                            </Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="请求头">
                            <Paragraph
                                code
                                copyable
                                style={{ maxHeight: 200, overflow: 'auto' }}
                            >
                                {JSON.stringify(selectedRequest.headers || {}, null, 2)}
                            </Paragraph>
                        </Descriptions.Item>
                        <Descriptions.Item label="请求体">
                            <Paragraph
                                code
                                copyable
                                ellipsis={{ rows: 8, expandable: true }}
                            >
                                {selectedRequest.body || '(无请求体)'}
                            </Paragraph>
                        </Descriptions.Item>
                        <Descriptions.Item label="创建时间">
                            {dayjs(selectedRequest.created_at).format('YYYY-MM-DD HH:mm:ss')}
                        </Descriptions.Item>
                        <Descriptions.Item label="更新时间">
                            {dayjs(selectedRequest.updated_at).format('YYYY-MM-DD HH:mm:ss')}
                        </Descriptions.Item>
                    </Descriptions>
                )}
            </Modal>
        </div>
    );
};

export default Requests; 