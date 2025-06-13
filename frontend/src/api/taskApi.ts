/**
 * 任务相关API服务
 */

import { api } from './client';
import type { Task, TaskFormData, TaskStatus } from '../types/task.d.ts';

// 后端返回的任务统计数据格式
export interface TaskStats {
    total: number;
    running: number;
    pending: number;
    completed: number;
    failed: number;
    stopped: number;
    scheduler_running_count?: number;
}

export interface TaskListParams {
    skip?: number;
    limit?: number;
    search?: string;
    status?: TaskStatus;
    task_type?: string;
    request_id?: number;
}

export const taskApi = {
    // 创建任务
    createTask: (taskData: TaskFormData): Promise<Task> => {
        return api.post<Task>('/tasks/', taskData);
    },

    // 获取任务列表
    getTasks: (params?: TaskListParams): Promise<Task[]> => {
        return api.get<Task[]>('/tasks/', params);
    },

    // 获取任务详情
    getTask: (taskId: number): Promise<Task> => {
        return api.get<Task>(`/tasks/${taskId}`);
    },

    // 更新任务
    updateTask: (taskId: number, taskData: Partial<TaskFormData>): Promise<Task> => {
        return api.put<Task>(`/tasks/${taskId}`, taskData);
    },

    // 删除任务
    deleteTask: (taskId: number): Promise<{ deleted_id: number }> => {
        return api.delete<{ deleted_id: number }>(`/tasks/${taskId}`);
    },

    // 启动任务
    startTask: (taskId: number): Promise<Task> => {
        return api.post<Task>(`/tasks/${taskId}/start`);
    },

    // 停止任务
    stopTask: (taskId: number): Promise<Task> => {
        return api.post<Task>(`/tasks/${taskId}/stop`);
    },

    // 复制任务
    duplicateTask: (taskId: number, newName: string): Promise<Task> => {
        return api.post<Task>(`/tasks/${taskId}/duplicate?new_name=${encodeURIComponent(newName)}`);
    },

    // 更新任务状态
    updateTaskStatus: (taskId: number, status: TaskStatus): Promise<Task> => {
        return api.post<Task>(`/tasks/${taskId}/status`, { status });
    },

    // 获取任务统计
    getTaskStats: (): Promise<TaskStats> => {
        return api.get<TaskStats>('/tasks/stats/summary');
    },
}; 