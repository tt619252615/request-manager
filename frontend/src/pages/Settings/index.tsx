import React from 'react';
import { Card, Form, Input, Switch, Button, InputNumber, Space } from 'antd';

const Settings: React.FC = () => {
    const [form] = Form.useForm();

    const onFinish = (values: any) => {
        console.log('设置保存:', values);
    };

    return (
        <div>
            <h1>系统设置</h1>

            <Card title="基础配置" style={{ marginBottom: 16 }}>
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                    initialValues={{
                        defaultTimeout: 30,
                        maxRetryAttempts: 10,
                        defaultThreadCount: 5,
                        enableLogging: true,
                        enableNotifications: false,
                    }}
                >
                    <Form.Item
                        label="默认请求超时时间 (秒)"
                        name="defaultTimeout"
                        rules={[{ required: true, message: '请输入超时时间' }]}
                    >
                        <InputNumber min={1} max={300} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item
                        label="默认最大重试次数"
                        name="maxRetryAttempts"
                        rules={[{ required: true, message: '请输入重试次数' }]}
                    >
                        <InputNumber min={1} max={100} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item
                        label="默认线程数"
                        name="defaultThreadCount"
                        rules={[{ required: true, message: '请输入线程数' }]}
                    >
                        <InputNumber min={1} max={50} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item
                        label="启用详细日志"
                        name="enableLogging"
                        valuePropName="checked"
                    >
                        <Switch />
                    </Form.Item>

                    <Form.Item
                        label="启用消息通知"
                        name="enableNotifications"
                        valuePropName="checked"
                    >
                        <Switch />
                    </Form.Item>

                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                保存设置
                            </Button>
                            <Button onClick={() => form.resetFields()}>
                                重置
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Card>

            <Card title="代理设置">
                <Form layout="vertical">
                    <Form.Item
                        label="代理服务器地址"
                        name="proxyUrl"
                    >
                        <Input placeholder="http://proxy.example.com:8080" />
                    </Form.Item>

                    <Form.Item
                        label="启用代理轮换"
                        name="enableProxyRotation"
                        valuePropName="checked"
                    >
                        <Switch />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary">
                            保存代理设置
                        </Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default Settings; 