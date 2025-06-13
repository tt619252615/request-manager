/**
 * HTTP API 客户端配置
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type { BaseResponse } from '../types/api';
import { ErrorCodes } from '../types/api';
import { message } from 'antd';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
    baseURL: '/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
apiClient.interceptors.request.use(
    (config) => {
        // 添加认证token（如果有）
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // 记录请求
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);

        return config;
    },
    (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
apiClient.interceptors.response.use(
    (response: AxiosResponse<BaseResponse>) => {
        const { data } = response;

        // 记录响应
        console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, data);

        // 检查业务状态码
        if (data.code !== ErrorCodes.SUCCESS) {
            const errorMsg = data.message || '请求失败';
            console.warn('⚠️ Business Error:', errorMsg);

            // 根据错误码处理不同的错误
            switch (data.code) {
                case ErrorCodes.UNAUTHORIZED:
                    message.error('未授权，请重新登录');
                    // 清除token并跳转到登录页
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                    break;
                case ErrorCodes.FORBIDDEN:
                    message.error('权限不足');
                    break;
                case ErrorCodes.NOT_FOUND:
                    message.error('资源不存在');
                    break;
                case ErrorCodes.PARAMETER_ERROR:
                    message.error(`参数错误: ${errorMsg}`);
                    break;
                default:
                    message.error(errorMsg);
            }

            return Promise.reject(new Error(errorMsg));
        }

        return response;
    },
    (error: AxiosError) => {
        console.error('❌ Response Error:', error);

        let errorMessage = '网络错误，请稍后重试';

        if (error.response) {
            // 服务器返回了错误状态码
            const { status, data } = error.response;

            switch (status) {
                case 400:
                    errorMessage = '请求参数错误';
                    break;
                case 401:
                    errorMessage = '未授权，请重新登录';
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                    break;
                case 403:
                    errorMessage = '权限不足';
                    break;
                case 404:
                    errorMessage = '请求的资源不存在';
                    break;
                case 500:
                    errorMessage = '服务器内部错误';
                    break;
                case 502:
                    errorMessage = '网关错误';
                    break;
                case 503:
                    errorMessage = '服务暂时不可用';
                    break;
                default:
                    errorMessage = (data as any)?.message || `服务器错误 (${status})`;
            }
        } else if (error.request) {
            // 网络错误
            errorMessage = '网络连接失败，请检查网络';
        } else {
            // 其他错误
            errorMessage = error.message || '未知错误';
        }

        message.error(errorMessage);
        return Promise.reject(error);
    }
);

// 导出API客户端
export default apiClient;

// 便捷方法 - 确保正确处理 BaseResponse 格式
export const api = {
    get: <T = any>(url: string, params?: any): Promise<T> =>
        apiClient.get<BaseResponse<T>>(url, { params })
            .then(res => {
                // 确保返回的数据结构正确
                if (res.data && res.data.data !== undefined) {
                    return res.data.data;
                }
                // 如果data字段为null或undefined，返回null
                return null as T;
            }),

    post: <T = any>(url: string, data?: any): Promise<T> =>
        apiClient.post<BaseResponse<T>>(url, data)
            .then(res => {
                if (res.data && res.data.data !== undefined) {
                    return res.data.data;
                }
                return null as T;
            }),

    put: <T = any>(url: string, data?: any): Promise<T> =>
        apiClient.put<BaseResponse<T>>(url, data)
            .then(res => {
                if (res.data && res.data.data !== undefined) {
                    return res.data.data;
                }
                return null as T;
            }),

    delete: <T = any>(url: string): Promise<T> =>
        apiClient.delete<BaseResponse<T>>(url)
            .then(res => {
                if (res.data && res.data.data !== undefined) {
                    return res.data.data;
                }
                return null as T;
            }),

    patch: <T = any>(url: string, data?: any): Promise<T> =>
        apiClient.patch<BaseResponse<T>>(url, data)
            .then(res => {
                if (res.data && res.data.data !== undefined) {
                    return res.data.data;
                }
                return null as T;
            }),

    // 直接返回完整响应的方法（用于需要访问message等字段的场景）
    getRaw: <T = any>(url: string, params?: any): Promise<BaseResponse<T>> =>
        apiClient.get<BaseResponse<T>>(url, { params }).then(res => res.data),

    postRaw: <T = any>(url: string, data?: any): Promise<BaseResponse<T>> =>
        apiClient.post<BaseResponse<T>>(url, data).then(res => res.data),

    putRaw: <T = any>(url: string, data?: any): Promise<BaseResponse<T>> =>
        apiClient.put<BaseResponse<T>>(url, data).then(res => res.data),

    deleteRaw: <T = any>(url: string): Promise<BaseResponse<T>> =>
        apiClient.delete<BaseResponse<T>>(url).then(res => res.data),
};

// 导出client别名，保持向后兼容
export const client = api; 