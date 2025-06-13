/**
 * 任务相关类型定义
 */

import { HttpRequest } from './request';

// 任务类型
export type TaskType = 'single' | 'scheduled' | 'retry';

// 任务状态
export type TaskStatus = 'pending' | 'running' | 'stopped' | 'completed' | 'failed';

// 调度类型
export type ScheduleType = 'immediate' | 'datetime' | 'cron';

// 调度配置
export interface ScheduleConfig {
    type: ScheduleType;
    start_time?: string;
    cron_expression?: string;
    timezone?: string;
}

// 重试配置
export interface RetryConfig {
    max_attempts: number;
    interval_seconds: number;
    success_condition?: string;  // 成功条件表达式
    stop_condition?: string;     // 停止条件表达式
    key_message?: string;        // 关键消息
}

// 代理配置
export interface ProxyConfig {
    enabled: boolean;
    proxy_url?: string;
    rotation: boolean;
    timeout: number;
}

// 任务定义
export interface Task {
    id: number;
    name: string;
    description?: string;
    request_id: number;
    request?: HttpRequest;  // 关联的请求
    task_type: TaskType;
    schedule_config: ScheduleConfig;
    retry_config: RetryConfig;
    proxy_config: ProxyConfig;
    status: TaskStatus;
    thread_count: number;
    time_diff: number;
    execution_count: number;
    success_count: number;
    failure_count: number;
    last_execution_at?: string;
    next_execution_at?: string;
    created_at: string;
    updated_at: string;
}

// 任务创建/更新的表单数据
export interface TaskFormData {
    name: string;
    description?: string;
    request_id: number;
    task_type: TaskType;
    schedule_config: ScheduleConfig;
    retry_config: RetryConfig;
    proxy_config: ProxyConfig;
    thread_count: number;
    time_diff: number;

    // 调度相关字段
    schedule_start_time?: string;
    cron_expression?: string;

    // 重试配置字段
    max_attempts?: number;
    interval_seconds?: number;
    success_condition?: string;
    stop_condition?: string;
    key_message?: string;

    // 代理配置字段
    proxy_enabled?: boolean;
    proxy_url?: string;
    proxy_rotation?: boolean;
    proxy_timeout?: number;
}

// 执行记录
export interface ExecutionRecord {
    id: number;
    task_id: number;
    request_id: number;
    status: 'success' | 'failed' | 'timeout';
    response_code?: number;
    response_body?: string;
    response_time?: number;
    error_message?: string;
    executed_at: string;
} 