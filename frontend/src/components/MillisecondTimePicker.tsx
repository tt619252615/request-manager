import React, { useState, useEffect } from 'react';
import { TimePicker, InputNumber, Space, Button, Card, Typography, message } from 'antd';
import { SyncOutlined, ClockCircleOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { systemApi, type NetworkTimeInfo } from '@/api/systemApi';

const { Text } = Typography;

export interface MillisecondTimePickerProps {
    value?: string;
    onChange?: (value: string) => void;
    placeholder?: string;
    format?: string;
    allowClear?: boolean;
    disabled?: boolean;
    showNetworkTime?: boolean;
}

const MillisecondTimePicker: React.FC<MillisecondTimePickerProps> = ({
    value,
    onChange,
    placeholder = "选择时间（毫秒精度）",
    format = "HH:mm:ss",
    allowClear = true,
    disabled = false,
    showNetworkTime = true,
}) => {
    const [timeValue, setTimeValue] = useState<Dayjs | null>(null);
    const [milliseconds, setMilliseconds] = useState<number>(0);
    const [networkTime, setNetworkTime] = useState<NetworkTimeInfo | null>(null);
    const [loading, setLoading] = useState(false);

    // 解析输入值
    useEffect(() => {
        if (value) {
            try {
                // 支持多种格式: HH:mm:ss.SSS, HH:mm:ss, 等
                const timeRegex = /^(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?$/;
                const match = value.match(timeRegex);

                if (match) {
                    const [, hours, minutes, seconds, ms] = match;
                    const timeStr = `${hours}:${minutes}:${seconds}`;
                    const parsed = dayjs(timeStr, 'HH:mm:ss');

                    if (parsed.isValid()) {
                        setTimeValue(parsed);
                        setMilliseconds(ms ? parseInt(ms.padEnd(3, '0')) : 0);
                    }
                } else {
                    // 尝试dayjs解析
                    const parsed = dayjs(value, format);
                    if (parsed.isValid()) {
                        setTimeValue(parsed);
                        setMilliseconds(0);
                    }
                }
            } catch (error) {
                console.warn('时间解析失败:', error);
            }
        } else {
            setTimeValue(null);
            setMilliseconds(0);
        }
    }, [value, format]);

    // 获取网络时间
    const fetchNetworkTime = async () => {
        if (!showNetworkTime) return;

        try {
            setLoading(true);
            const data = await systemApi.getNetworkTime();
            setNetworkTime(data);
        } catch (error: any) {
            console.error('获取网络时间失败:', error);
            message.error('获取网络时间失败');
        } finally {
            setLoading(false);
        }
    };

    // 同步网络时间
    const syncNetworkTime = async () => {
        try {
            setLoading(true);
            await systemApi.syncNetworkTime();
            await fetchNetworkTime();
            message.success('网络时间同步成功');
        } catch (error: any) {
            console.error('同步网络时间失败:', error);
            message.error('同步网络时间失败');
        } finally {
            setLoading(false);
        }
    };

    // 使用当前网络时间
    const useNetworkTime = () => {
        if (networkTime) {
            // 解析网络时间的时分秒毫秒部分
            const timeRegex = /(\d{2}):(\d{2}):(\d{2})\.(\d{3})/;
            const match = networkTime.formatted_time.match(timeRegex);

            if (match) {
                const [, hours, minutes, seconds, ms] = match;
                const timeStr = `${hours}:${minutes}:${seconds}`;
                const parsed = dayjs(timeStr, 'HH:mm:ss');

                setTimeValue(parsed);
                setMilliseconds(parseInt(ms));

                // 触发onChange
                const fullTimeStr = `${timeStr}.${ms}`;
                onChange?.(fullTimeStr);
            }
        }
    };

    // 初始化获取网络时间
    useEffect(() => {
        fetchNetworkTime();
    }, []);

    // 处理时间变化
    const handleTimeChange = (time: Dayjs | null) => {
        setTimeValue(time);

        if (time) {
            const timeStr = time.format('HH:mm:ss');
            const fullTimeStr = milliseconds > 0
                ? `${timeStr}.${milliseconds.toString().padStart(3, '0')}`
                : timeStr;
            onChange?.(fullTimeStr);
        } else {
            onChange?.('');
        }
    };

    // 处理毫秒变化
    const handleMillisecondsChange = (ms: number | null) => {
        const newMs = ms || 0;
        setMilliseconds(newMs);

        if (timeValue) {
            const timeStr = timeValue.format('HH:mm:ss');
            const fullTimeStr = newMs > 0
                ? `${timeStr}.${newMs.toString().padStart(3, '0')}`
                : timeStr;
            onChange?.(fullTimeStr);
        }
    };

    return (
        <div>
            <Space direction="vertical" style={{ width: '100%' }}>
                {/* 时间选择器 */}
                <Space>
                    <TimePicker
                        value={timeValue}
                        onChange={handleTimeChange}
                        format={format}
                        placeholder={placeholder}
                        allowClear={allowClear}
                        disabled={disabled}
                        showNow
                        style={{ width: 120 }}
                    />
                    <span>.</span>
                    <InputNumber
                        value={milliseconds}
                        onChange={handleMillisecondsChange}
                        min={0}
                        max={999}
                        placeholder="毫秒"
                        disabled={disabled}
                        style={{ width: 80 }}
                        formatter={(value) => value?.toString().padStart(3, '0') || '000'}
                        parser={(value) => {
                            const num = parseInt(value?.replace(/\D/g, '') || '0');
                            return Math.min(999, Math.max(0, num));
                        }}
                    />
                </Space>

                {/* 网络时间信息 */}
                {showNetworkTime && (
                    <Card size="small" style={{ marginTop: 8 }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                            <Space>
                                <ClockCircleOutlined />
                                <Text strong>网络时间参考</Text>
                                <Button
                                    type="link"
                                    size="small"
                                    icon={<SyncOutlined spin={loading} />}
                                    onClick={syncNetworkTime}
                                    loading={loading}
                                >
                                    同步
                                </Button>
                            </Space>

                            {networkTime && (
                                <Space direction="vertical" size="small">
                                    <Text type="secondary">
                                        当前网络时间: {networkTime.formatted_time}
                                    </Text>
                                    <Text type="secondary">
                                        时间差: {networkTime.time_diff > 0 ? '+' : ''}{networkTime.time_diff.toFixed(3)}秒
                                    </Text>
                                    <Button
                                        type="dashed"
                                        size="small"
                                        onClick={useNetworkTime}
                                        disabled={disabled}
                                    >
                                        使用当前网络时间
                                    </Button>
                                </Space>
                            )}
                        </Space>
                    </Card>
                )}
            </Space>
        </div>
    );
};

export default MillisecondTimePicker; 