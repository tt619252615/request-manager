/**
 * 执行记录相关API服务
 */

import { api } from './client';

// 执行记录状态
export type ExecutionStatus = 'success' | 'failed' | 'timeout' | 'running';

// 执行记录接口
export interface ExecutionRecord {
    id: number;
    task_id: number;
    request_id: number;
    status: ExecutionStatus;
    request_url: string;
    request_headers?: Record<string, string>;
    request_body?: string;
    proxy_used?: string;
    response_code?: number;
    response_headers?: Record<string, string>;
    response_body?: string;
    response_time?: number;
    error_message?: string;
    thread_id?: string;
    attempt_number: number;
    execution_time: string;
    created_at: string;
}

// 查询参数
export interface ExecutionListParams {
    skip?: number;
    limit?: number;
    task_id?: number;
    request_id?: number;
    status?: ExecutionStatus;
    start_time?: string;
    end_time?: string;
}

// 执行统计
export interface ExecutionStats {
    total: number;
    success: number;
    failed: number;
    timeout: number;
    avg_response_time?: number;
    success_rate: number;
}

export const executionApi = {
    // 获取执行记录列表
    getExecutions: (params?: ExecutionListParams): Promise<ExecutionRecord[]> => {
        return api.get<ExecutionRecord[]>('/executions/', params);
    },

    // 获取执行记录详情
    getExecution: (executionId: number): Promise<ExecutionRecord> => {
        return api.get<ExecutionRecord>(`/executions/${executionId}`);
    },

    // 获取任务执行记录
    getTaskExecutions: (taskId: number, params?: Omit<ExecutionListParams, 'task_id'>): Promise<ExecutionRecord[]> => {
        return api.get<ExecutionRecord[]>(`/executions/task/${taskId}`, params);
    },

    // 获取执行统计
    getExecutionStats: (params?: { task_id?: number; request_id?: number }): Promise<ExecutionStats> => {
        return api.get<ExecutionStats>('/executions/stats', params);
    },

    // 删除执行记录
    deleteExecution: (executionId: number): Promise<{ deleted_id: number }> => {
        return api.delete<{ deleted_id: number }>(`/executions/${executionId}`);
    },

    // 清理执行记录
    cleanupExecutions: (params: { before_date?: string; keep_latest?: number }): Promise<{ deleted_count: number }> => {
        return api.post<{ deleted_count: number }>('/executions/cleanup', params);
    },
}; 