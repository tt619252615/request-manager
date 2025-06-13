/**
 * 请求相关API服务
 */

import { api } from './client';
import type { HttpRequest } from '../types/request.d.ts';

export interface FiddlerImportData {
    raw_data: string;
    name: string;
    description?: string;
}

export interface RequestListParams {
    skip?: number;
    limit?: number;
    search?: string;
    method?: string;
}

export const requestApi = {
    // 从Fiddler Raw格式导入请求
    importFromFiddler: (data: FiddlerImportData): Promise<HttpRequest> => {
        return api.post<HttpRequest>('/requests/import/fiddler', data);
    },

    // 获取请求列表
    getRequests: (params?: RequestListParams): Promise<HttpRequest[]> => {
        return api.get<HttpRequest[]>('/requests/', params);
    },

    // 获取请求详情
    getRequest: (requestId: number): Promise<HttpRequest> => {
        return api.get<HttpRequest>(`/requests/${requestId}`);
    },

    // 创建请求
    createRequest: (requestData: Partial<HttpRequest>): Promise<HttpRequest> => {
        return api.post<HttpRequest>('/requests/', requestData);
    },

    // 更新请求
    updateRequest: (requestId: number, requestData: Partial<HttpRequest>): Promise<HttpRequest> => {
        return api.put<HttpRequest>(`/requests/${requestId}`, requestData);
    },

    // 删除请求
    deleteRequest: (requestId: number): Promise<{ deleted_id: number }> => {
        return api.delete<{ deleted_id: number }>(`/requests/${requestId}`);
    },

    // 测试请求
    testRequest: (requestId: number): Promise<any> => {
        return api.post<any>(`/requests/${requestId}/test`);
    },
}; 