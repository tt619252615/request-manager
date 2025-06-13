import React, { useState } from 'react';
import { Modal, Form, Input, Button, message, Tabs, Alert } from 'antd';
import { parseFiddlerRaw, parseCurl, validateParsedRequest, toHttpRequest } from '@/utils/parser';
import type { HttpRequest } from '@/types/request';

const { TextArea } = Input;

interface ImportModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess: (request: Omit<HttpRequest, 'id' | 'created_at' | 'updated_at'>) => void;
}

const ImportModal: React.FC<ImportModalProps> = ({ visible, onCancel, onSuccess }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [previewData, setPreviewData] = useState<any>(null);
    const [activeTab, setActiveTab] = useState('fiddler');

    const handlePreview = () => {
        const values = form.getFieldsValue();
        const { rawData, name, description } = values;

        if (!rawData?.trim()) {
            message.error('请输入要解析的数据');
            return;
        }

        try {
            let parsed;
            if (activeTab === 'fiddler') {
                parsed = parseFiddlerRaw(rawData);
            } else {
                parsed = parseCurl(rawData);
            }

            const validation = validateParsedRequest(parsed);
            if (!validation.valid) {
                message.error(`解析失败: ${validation.errors.join(', ')}`);
                return;
            }

            const request = toHttpRequest(parsed, name || '导入的请求', description);
            setPreviewData(request);
            message.success('解析成功！请检查预览数据');
        } catch (error) {
            message.error(`解析失败: ${error instanceof Error ? error.message : '未知错误'}`);
            setPreviewData(null);
        }
    };

    const handleSubmit = async () => {
        if (!previewData) {
            message.error('请先预览解析结果');
            return;
        }

        setLoading(true);
        try {
            onSuccess(previewData);
            form.resetFields();
            setPreviewData(null);
            message.success('导入成功！');
        } catch (error) {
            message.error('导入失败');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        form.resetFields();
        setPreviewData(null);
        onCancel();
    };

    // 示例数据
    const fiddlerExample = `POST https://rights-apigw.meituan.com/api/rights/activity/secKill/grab?cType=mtiphone&fpPlatform=5&wx_openid=&appVersion=12.35.401&gdBs=0000&pageVersion=1749257933402&yodaReady=h5&csecplatform=4&csecversion=3.2.0 HTTP/2
host: rights-apigw.meituan.com
content-type: application/json
x-titans-user: 
accept: application/json, text/plain, */*
sec-fetch-site: same-site
origin: https://market.waimai.meituan.com
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/18.3.2
referer: https://market.waimai.meituan.com/
content-length: 1642

{"activityId":"A1930104757016543294","gdId":601664,"pageId":618337,"instanceId":"17490090128760.4805414218792613","rightCode":"R1930108317557674036","roundCode":"ROUND1930109662054244380","grabToken":"13418068095eb56a01959315e202d69d","mtFingerprint":"i2HKpOmsirDPavelVfQBZMuuHn/EPK3O2hg5MxEB8dJ3I56a+QKRiTxwwQZzWBaAPPhR1dlTgeXl/t4luI4HNsfWZPNIz6xtM+7DYJuUveIgqNS/oM1Su8PJ4ELhOnvMwH8iqbe2oVXJjjds7DqoHsnhyRulfpEpROlOOTSRiPg21Oe1KD4UYDvlgrrZ1Is3/c+wxdV24TsUKXUyLRpf0kEbTBJQ2UqNrHyMAfh/5Uwdvg66dSpPqx2s/sgRuack5Idq+yfqTMjGglQGyIziLKGpIPjirjzR+mIH1s3mD05GVqxmZxKuzIpQujVGc6inZVI6lX/RR4043zxgR6jOa1AiYSJQZzefU8o+f6crgVLWAdvDhpeCiooc5zZaRRxNEft/ElUUteGe8FIcCZVZhK+pyfevMHXM2/IwqbCEi25kD9uAjWX3de4cnO8X2iiTtq6BWaSadOrivmG4bKY/M/iqxunIFa7tbk1DKXuauKKVzEeldXCg31HRZ7PBMy7Wdz+ZUL4Gv3lH/jEtqKXssMM16D8qkszPv9X+4M+g2ZmcruzJQSu/NvddCxc/G5mcQWKBvXa6Q+JM7OlsVBO6WpBzWcfcTfUtqx06+chwHBajsqRp1sXqmQ8hPWoJjVxuZUzzJ594rALNq9mfP7u7AzyLTWY1zO+cFvqpRXxTvQgU5JmoiuXXdWdMatGAA+bP/cVTWix/k8XU/q7iXq7a3NOVWM0+J+762l3K0IMPJK2Uu4xxupvOUDcl3YewnvvmWQYv9N1YRq9r7xuYSnD4Uq0+mNJaVL7Yt7B/lgOVqu/n8U8oIOFjUouKrbVAb2xxuw/lLk+t7jdBsjEB2wIEzd2KZcbYdHsAGb7o3Vy8lndTHhUQTMWWHdE1oGfMv+2kHw8tcTinY5v5VHEIOOSrhL9KRRrha5gbPBoR1id8aYmEt70JNQKyTDFwrU3tEVzEpILHzmUH6iZzlKkj9QG4OmUsMUOucO5VKVvaLIXFL9S7vl4VDI5Sl/HOZexz/8UaLUWyOKa9zSoiWmUPN2vCrgzu3DW1TpCPNoPj06NKz2LwOHKcYeBq7PTdVM2smetDZjGebUVJTVvGwx1eMpnppclIMn+GJm78W64Qov+j8Db0g5dkIGYfHL2wBorgI9nXI5ETbEy3hq+GCo6SMXf7abqx6SJT+SYeqC/4hHPM4/LDV0h3N49nwmg3ovRbb1rjsdNe83JAgN6Fa0JSsOVFJkfKHEZ1oeuUfZiCy1OV037iywrD9S48Ojl1PVyOdYLbYbFiciEVeeqqFVLzScAIYtqhDAiCkPC7mGESpcJY7ZE8Q23UrGfFKFNfsdueMbHNY3wPTpac5WX+8JTb9o/mgazRuyrvbZvmfxaTAkConRo="}`;

    const curlExample = `curl -X POST 'https://api.example.com/data' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer token123' \\
  -d '{"key": "value"}'`;

    const tabItems = [
        {
            key: 'fiddler',
            label: 'Fiddler Raw',
            children: (
                <div>
                    <Alert
                        message="Fiddler Raw 格式说明"
                        description="请粘贴从 Fiddler 复制的完整 HTTP 请求数据，包括请求行、请求头和请求体。"
                        type="info"
                        style={{ marginBottom: 16 }}
                    />
                    <Form.Item
                        name="rawData"
                        rules={[{ required: true, message: '请输入 Fiddler Raw 数据' }]}
                    >
                        <TextArea
                            rows={12}
                            placeholder={`示例格式：\n${fiddlerExample.substring(0, 300)}...`}
                        />
                    </Form.Item>
                </div>
            ),
        },
        {
            key: 'curl',
            label: 'cURL 命令',
            children: (
                <div>
                    <Alert
                        message="cURL 命令格式说明"
                        description="请粘贴完整的 cURL 命令，支持多行格式。"
                        type="info"
                        style={{ marginBottom: 16 }}
                    />
                    <Form.Item
                        name="rawData"
                        rules={[{ required: true, message: '请输入 cURL 命令' }]}
                    >
                        <TextArea
                            rows={12}
                            placeholder={`示例格式：\n${curlExample}`}
                        />
                    </Form.Item>
                </div>
            ),
        },
    ];

    return (
        <Modal
            title="导入 HTTP 请求"
            open={visible}
            onCancel={handleCancel}
            width={800}
            footer={[
                <Button key="cancel" onClick={handleCancel}>
                    取消
                </Button>,
                <Button key="preview" onClick={handlePreview}>
                    预览解析
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    loading={loading}
                    onClick={handleSubmit}
                    disabled={!previewData}
                >
                    确认导入
                </Button>,
            ]}
        >
            <Form form={form} layout="vertical">
                <Form.Item
                    label="请求名称"
                    name="name"
                    rules={[{ required: true, message: '请输入请求名称' }]}
                >
                    <Input placeholder="请输入请求名称" />
                </Form.Item>

                <Form.Item label="请求描述" name="description">
                    <Input placeholder="请输入请求描述（可选）" />
                </Form.Item>

                <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    items={tabItems}
                />

                {previewData && (
                    <div style={{ marginTop: 16 }}>
                        <Alert
                            message="解析预览"
                            description={
                                <div>
                                    <p><strong>方法:</strong> {previewData.method}</p>
                                    <p><strong>URL:</strong> {previewData.url}</p>
                                    <p><strong>请求头数量:</strong> {Object.keys(previewData.headers).length}</p>
                                    <p><strong>查询参数数量:</strong> {Object.keys(previewData.params || {}).length}</p>
                                    {previewData.body && <p><strong>请求体:</strong> 已包含</p>}
                                </div>
                            }
                            type="success"
                        />
                    </div>
                )}
            </Form>
        </Modal>
    );
};

export default ImportModal; 