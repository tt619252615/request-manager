import React, { useState } from 'react';
import { Modal, Form, Input, message } from 'antd';
import { requestApi } from '@/api/requestApi';
import type { HttpRequest } from '@/types/request';

const { TextArea } = Input;

interface FiddlerImportModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess: (request: HttpRequest) => void;
}

const FiddlerImportModal: React.FC<FiddlerImportModalProps> = ({
    visible,
    onCancel,
    onSuccess,
}) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        try {
            setLoading(true);
            const values = await form.validateFields();

            const result = await requestApi.importFromFiddler({
                raw_data: values.raw_data,
                name: values.name,
                description: values.description,
            });

            message.success('导入成功');
            onSuccess(result);
            form.resetFields();
        } catch (error: any) {
            console.error('导入失败:', error);
            message.error(error.message || '导入失败');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        form.resetFields();
        onCancel();
    };

    return (
        <Modal
            title="导入Fiddler请求"
            open={visible}
            onCancel={handleCancel}
            onOk={handleSubmit}
            confirmLoading={loading}
            width={800}
            destroyOnClose
        >
            <Form form={form} layout="vertical">
                <Form.Item
                    name="name"
                    label="请求名称"
                    rules={[{ required: true, message: '请输入请求名称' }]}
                >
                    <Input placeholder="请输入请求名称" />
                </Form.Item>

                <Form.Item name="description" label="请求描述">
                    <Input placeholder="请输入请求描述" />
                </Form.Item>

                <Form.Item
                    name="raw_data"
                    label="Fiddler Raw数据"
                    rules={[{ required: true, message: '请粘贴Fiddler Raw数据' }]}
                >
                    <TextArea
                        rows={15}
                        placeholder="请粘贴从Fiddler复制的Raw数据，包含完整的HTTP请求头和请求体"
                        style={{ fontFamily: 'monospace' }}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
};

export default FiddlerImportModal; 