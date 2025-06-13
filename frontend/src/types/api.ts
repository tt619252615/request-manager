/**
 * API 响应类型定义
 * 与后端 schemas/response.py 保持一致
 */

// 基础响应类型
export interface BaseResponse<T = any> {
    code: number;
    data: T;
    message: string;
    timestamp: number;
}

// 分页信息
export interface PaginationInfo {
    page: number;
    size: number;
    total: number;
    pages: number;
}

// 分页数据
export interface PaginatedData<T> {
    items: T[];
    pagination: PaginationInfo;
}

// 分页响应
export type PaginatedResponse<T> = BaseResponse<PaginatedData<T>>;

// 成功响应
export type SuccessResponse<T = any> = BaseResponse<T>;

// 错误响应
export type ErrorResponse = BaseResponse<null>;

// 错误码定义 - 使用普通enum而不是const enum
export enum ErrorCodes {
    // 通用错误码
    SUCCESS = 0,
    UNKNOWN_ERROR = -1,
    PARAMETER_ERROR = -2,
    UNAUTHORIZED = -3,
    FORBIDDEN = -4,
    NOT_FOUND = -5,
    METHOD_NOT_ALLOWED = -6,
    INTERNAL_ERROR = -7,

    // 业务错误码
    REQUEST_NOT_FOUND = 1001,
    REQUEST_INVALID = 1002,
    REQUEST_EXECUTION_FAILED = 1003,

    TASK_NOT_FOUND = 2001,
    TASK_INVALID = 2002,
    TASK_ALREADY_RUNNING = 2003,
    TASK_NOT_RUNNING = 2004,

    EXECUTION_NOT_FOUND = 3001,
    EXECUTION_FAILED = 3002,

    // 解析错误码
    PARSE_ERROR = 4001,
    INVALID_FORMAT = 4002,
} 