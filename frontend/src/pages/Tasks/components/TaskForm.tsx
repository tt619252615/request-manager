import React, { useState, useEffect } from 'react';
import {
    Modal,
    Form,
    Input,
    Select,
    InputNumber,
    Switch,
    Space,
    message,
    Tabs,
} from 'antd';
import { requestApi } from '@/api/requestApi';
import { taskApi } from '@/api/taskApi';
import type { Task, TaskFormData, ScheduleType } from '@/types/task';
import type { HttpRequest } from '@/types/request';
import MillisecondTimePicker from '@/components/MillisecondTimePicker';

const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

interface TaskFormProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess: (task: Task) => void;
    editingTask?: Task | null;
}

const TaskForm: React.FC<TaskFormProps> = ({
    visible,
    onCancel,
    onSuccess,
    editingTask,
}) => {
    const [form] = Form.useForm<TaskFormData>();
    const [loading, setLoading] = useState(false);
    const [requests, setRequests] = useState<HttpRequest[]>([]);
    const [scheduleType, setScheduleType] = useState<ScheduleType>('immediate');
    const [activeTab, setActiveTab] = useState<string>('basic');

    // 加载请求列表
    useEffect(() => {
        if (visible) {
            loadRequests();
        }
    }, [visible]);

    // 编辑时填充表单
    useEffect(() => {
        if (editingTask && visible) {
            console.log('🔧 正在编辑任务:', editingTask);

            // 解析配置数据
            const scheduleConfig = editingTask.schedule_config || {};
            const retryConfig = editingTask.retry_config || {};
            const proxyConfig = editingTask.proxy_config || {};

            const formData = {
                // 基本信息
                name: editingTask.name,
                description: editingTask.description,
                request_id: editingTask.request_id,
                task_type: editingTask.task_type,
                thread_count: editingTask.thread_count ?? 1,
                time_diff: editingTask.time_diff ?? 0,

                // 调度配置 - 支持毫秒级时间
                schedule_start_time: scheduleConfig.start_time || undefined,
                cron_expression: scheduleConfig.cron_expression,

                // 重试配置
                max_attempts: retryConfig.max_attempts ?? 10,
                interval_seconds: retryConfig.interval_seconds !== undefined && retryConfig.interval_seconds !== null ? retryConfig.interval_seconds : 5,
                success_condition: retryConfig.success_condition,
                stop_condition: retryConfig.stop_condition,
                key_message: retryConfig.key_message,

                // 代理配置
                proxy_enabled: proxyConfig.enabled ?? false,
                proxy_url: proxyConfig.proxy_url,
                proxy_rotation: proxyConfig.rotation !== false,
                proxy_timeout: proxyConfig.timeout ?? 30,
            };

            console.log('📝 填充表单数据:', formData);
            form.setFieldsValue(formData);
            setScheduleType(scheduleConfig.type || 'immediate');
        } else if (visible) {
            // 新建时重置表单
            console.log('✨ 创建新任务，重置表单');
            form.resetFields();
            setScheduleType('immediate');
        }
    }, [editingTask, visible, form]);

    const loadRequests = async () => {
        try {
            const data = await requestApi.getRequests();
            setRequests(data);
        } catch (error) {
            message.error('加载请求列表失败');
        }
    };

    const handleSubmit = async () => {
        try {
            setLoading(true);
            const values = await form.validateFields();

            // 构建任务数据
            const taskData: TaskFormData = {
                name: values.name,
                description: values.description,
                request_id: values.request_id,
                task_type: values.task_type,
                thread_count: values.thread_count ?? 1,
                time_diff: values.time_diff ?? 0,
                schedule_config: {
                    type: scheduleType,
                    start_time: values.schedule_start_time || undefined,  // 直接使用字符串，支持毫秒级
                    cron_expression: values.cron_expression,
                    timezone: 'Asia/Shanghai',
                },
                retry_config: {
                    max_attempts: values.max_attempts ?? 10,
                    interval_seconds: values.interval_seconds !== undefined && values.interval_seconds !== null ? values.interval_seconds : 5,
                    success_condition: values.success_condition,
                    stop_condition: values.stop_condition,
                    key_message: values.key_message,
                },
                proxy_config: {
                    enabled: values.proxy_enabled ?? false,
                    proxy_url: values.proxy_url,
                    rotation: values.proxy_rotation ?? true,
                    timeout: values.proxy_timeout ?? 30,
                },
            };

            let result: Task;
            if (editingTask) {
                result = await taskApi.updateTask(editingTask.id, taskData);
                message.success('任务更新成功');
            } else {
                result = await taskApi.createTask(taskData);
                message.success('任务创建成功');
            }

            onSuccess(result);
        } catch (error: any) {
            console.error('提交任务失败:', error);
            message.error(error.message || '操作失败');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            title={editingTask ? '编辑任务' : '新建任务'}
            open={visible}
            onCancel={onCancel}
            onOk={handleSubmit}
            confirmLoading={loading}
            width={800}
            destroyOnClose
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={{
                    task_type: 'single',
                    thread_count: 1,
                    time_diff: 0,
                    max_attempts: 10,
                    interval_seconds: 5,
                    proxy_enabled: false,
                    proxy_rotation: true,
                    proxy_timeout: 30,
                }}
            >
                <Tabs activeKey={activeTab} onChange={setActiveTab}>
                    <TabPane tab="基本配置" key="basic">
                        <Form.Item
                            name="name"
                            label="任务名称"
                            rules={[{ required: true, message: '请输入任务名称' }]}
                        >
                            <Input placeholder="请输入任务名称" />
                        </Form.Item>

                        <Form.Item name="description" label="任务描述">
                            <TextArea rows={3} placeholder="请输入任务描述" />
                        </Form.Item>

                        <Form.Item
                            name="request_id"
                            label="关联请求"
                            rules={[{ required: true, message: '请选择关联请求' }]}
                        >
                            <Select placeholder="请选择关联请求" showSearch>
                                {requests.map((req) => (
                                    <Option key={req.id} value={req.id}>
                                        {req.name} ({req.method} {req.url})
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="task_type"
                            label="任务类型"
                            rules={[{ required: true, message: '请选择任务类型' }]}
                        >
                            <Select>
                                <Option value="single">单次执行</Option>
                                <Option value="scheduled">定时任务</Option>
                                <Option value="retry">循环重试</Option>
                            </Select>
                        </Form.Item>

                        <Space>
                            <Form.Item name="thread_count" label="线程数">
                                <InputNumber min={1} max={50} />
                            </Form.Item>
                            <Form.Item name="time_diff" label="时间差(秒)">
                                <InputNumber />
                            </Form.Item>
                        </Space>
                    </TabPane>

                    <TabPane tab="调度配置" key="schedule">
                        <Form.Item label="调度类型">
                            <Select
                                value={scheduleType}
                                onChange={setScheduleType}
                            >
                                <Option value="immediate">立即执行</Option>
                                <Option value="datetime">指定时间</Option>
                                <Option value="cron">Cron表达式</Option>
                            </Select>
                        </Form.Item>

                        {scheduleType === 'datetime' && (
                            <Form.Item
                                name="schedule_start_time"
                                label="执行时间"
                                rules={[{ required: true, message: '请选择执行时间' }]}
                                tooltip="支持毫秒级精度，格式如：09:59:59.250"
                            >
                                <MillisecondTimePicker
                                    placeholder="请选择精确执行时间"
                                    showNetworkTime={true}
                                />
                            </Form.Item>
                        )}

                        {scheduleType === 'cron' && (
                            <Form.Item
                                name="cron_expression"
                                label="Cron表达式"
                                rules={[{ required: true, message: '请输入Cron表达式' }]}
                            >
                                <Input placeholder="例：0 0 12 * * ? (每天12点执行)" />
                            </Form.Item>
                        )}
                    </TabPane>

                    <TabPane tab="重试配置" key="retry">
                        <Space>
                            <Form.Item name="max_attempts" label="最大尝试次数">
                                <InputNumber min={1} max={1000} />
                            </Form.Item>
                            <Form.Item name="interval_seconds" label="重试间隔(秒)">
                                <InputNumber min={0} max={3600} />
                            </Form.Item>
                        </Space>

                        <Form.Item
                            name="success_condition"
                            label="成功条件表达式"
                            tooltip="留空时默认HTTP状态码2xx为成功，否则按表达式判断"
                        >
                            <Input
                                placeholder="例：response.status_code == 200 或 response_body.contains('success')"
                                allowClear
                            />
                        </Form.Item>

                        <Form.Item
                            name="stop_condition"
                            label="停止条件表达式"
                            tooltip="满足此条件时强制停止任务并标记为失败"
                        >
                            <Input
                                placeholder="例：response_body.contains('已售罄') 或 response.status_code == 403"
                                allowClear
                            />
                        </Form.Item>

                        <Form.Item
                            name="key_message"
                            label="关键消息"
                            tooltip="响应中包含此关键字时认为成功（优先级高于成功条件）"
                        >
                            <Input
                                placeholder="例：success, ok, 抢购成功"
                                allowClear
                            />
                        </Form.Item>
                    </TabPane>

                    <TabPane tab="代理配置" key="proxy">
                        <Form.Item name="proxy_enabled" label="启用代理" valuePropName="checked">
                            <Switch />
                        </Form.Item>

                        <Form.Item
                            noStyle
                            shouldUpdate={(prevValues, currentValues) =>
                                prevValues.proxy_enabled !== currentValues.proxy_enabled
                            }
                        >
                            {({ getFieldValue }) =>
                                getFieldValue('proxy_enabled') && (
                                    <>
                                        <Form.Item name="proxy_url" label="代理获取URL">
                                            <Input placeholder="代理API地址" />
                                        </Form.Item>

                                        <Space>
                                            <Form.Item name="proxy_rotation" label="轮换代理" valuePropName="checked">
                                                <Switch />
                                            </Form.Item>
                                            <Form.Item name="proxy_timeout" label="超时时间(秒)">
                                                <InputNumber min={1} max={300} />
                                            </Form.Item>
                                        </Space>
                                    </>
                                )
                            }
                        </Form.Item>
                    </TabPane>
                </Tabs>
            </Form>
        </Modal>
    );
};

export default TaskForm; 