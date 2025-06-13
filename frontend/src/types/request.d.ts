/**
 * 请求相关类型定义
 */

// HTTP 方法类型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';

// HTTP 请求定义
export interface HttpRequest {
  id: number;
  name: string;
  description?: string;
  method: HttpMethod;
  url: string;
  headers: Record<string, string>;
  body?: string;
  params?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

// 请求创建/更新的表单数据
export interface RequestFormData {
  name: string;
  description?: string;
  method: HttpMethod;
  url: string;
  headers: Record<string, string>;
  body?: string;
  params?: Record<string, string>;
}

// 请求导入格式
export interface ImportFormat {
  type: 'fiddler' | 'curl' | 'postman';
  content: string;
}

// 请求测试结果
export interface RequestTestResult {
  success: boolean;
  status_code?: number;
  response_body?: string;
  response_headers?: Record<string, string>;
  response_time?: number;
  error_message?: string;
} 