/**
 * Fiddler 数据解析工具
 * 用于解析 Fiddler Raw 格式的 HTTP 请求数据
 */

import type { HttpRequest, HttpMethod } from '@/types/request';

export interface ParsedRequest {
    method: HttpMethod;
    url: string;
    headers: Record<string, string>;
    body?: string;
    params?: Record<string, string>;
}

/**
 * 解析 Fiddler Raw 格式的 HTTP 请求
 * @param rawData Fiddler 导出的原始数据
 * @returns 解析后的请求对象
 */
export function parseFiddlerRaw(rawData: string): ParsedRequest {
    const lines = rawData.trim().split('\n');

    if (lines.length === 0) {
        throw new Error('无效的请求数据');
    }

    // 解析请求行 (第一行)
    const requestLine = lines[0].trim();
    const requestMatch = requestLine.match(/^(\w+)\s+(.+?)\s+HTTP\/[\d.]+$/);

    if (!requestMatch) {
        throw new Error('无效的请求行格式');
    }

    const method = requestMatch[1].toUpperCase() as HttpMethod;
    const fullUrl = requestMatch[2];

    // 分离URL和查询参数
    const [baseUrl, queryString] = fullUrl.split('?');
    const params: Record<string, string> = {};

    if (queryString) {
        queryString.split('&').forEach(param => {
            const [key, value] = param.split('=');
            if (key) {
                params[decodeURIComponent(key)] = decodeURIComponent(value || '');
            }
        });
    }

    // 解析请求头
    const headers: Record<string, string> = {};
    let bodyStartIndex = -1;

    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();

        // 空行表示头部结束，后面是请求体
        if (line === '') {
            bodyStartIndex = i + 1;
            break;
        }

        const colonIndex = line.indexOf(':');
        if (colonIndex > 0) {
            const headerName = line.substring(0, colonIndex).trim();
            const headerValue = line.substring(colonIndex + 1).trim();
            headers[headerName] = headerValue;
        }
    }

    // 解析请求体
    let body: string | undefined;
    if (bodyStartIndex > 0 && bodyStartIndex < lines.length) {
        body = lines.slice(bodyStartIndex).join('\n').trim();
    }

    // 构建完整URL (包含host)
    const host = headers['host'] || headers['Host'];
    let url = baseUrl;

    if (host && !baseUrl.startsWith('http')) {
        // 判断是否使用HTTPS
        const isHttps = headers['origin']?.startsWith('https://') ||
            headers['referer']?.startsWith('https://') ||
            baseUrl.includes('443');
        url = `${isHttps ? 'https' : 'http'}://${host}${baseUrl}`;
    }

    return {
        method,
        url,
        headers,
        body,
        params,
    };
}

/**
 * 解析 cURL 命令
 * @param curlCommand cURL 命令字符串
 * @returns 解析后的请求对象
 */
export function parseCurl(curlCommand: string): ParsedRequest {
    // 简化的 cURL 解析实现
    const lines = curlCommand.split('\n').map(line => line.trim()).filter(line => line);

    let method: HttpMethod = 'GET';
    let url = '';
    const headers: Record<string, string> = {};
    let body: string | undefined;

    for (const line of lines) {
        if (line.startsWith('curl ')) {
            // 提取URL
            const urlMatch = line.match(/curl\s+(?:-[^\s]+\s+)*['"]?([^'"\s]+)['"]?/);
            if (urlMatch) {
                url = urlMatch[1];
            }
        } else if (line.includes('-X ') || line.includes('--request ')) {
            // 提取HTTP方法
            const methodMatch = line.match(/(?:-X|--request)\s+(\w+)/);
            if (methodMatch) {
                method = methodMatch[1].toUpperCase() as HttpMethod;
            }
        } else if (line.includes('-H ') || line.includes('--header ')) {
            // 提取请求头
            const headerMatch = line.match(/(?:-H|--header)\s+['"]([^'"]+)['"]?/);
            if (headerMatch) {
                const [key, ...valueParts] = headerMatch[1].split(':');
                if (key && valueParts.length > 0) {
                    headers[key.trim()] = valueParts.join(':').trim();
                }
            }
        } else if (line.includes('-d ') || line.includes('--data ')) {
            // 提取请求体
            const dataMatch = line.match(/(?:-d|--data)\s+['"]([^'"]+)['"]?/);
            if (dataMatch) {
                body = dataMatch[1];
            }
        }
    }

    if (!url) {
        throw new Error('无法从 cURL 命令中提取 URL');
    }

    // 分离URL和查询参数
    const [baseUrl, queryString] = url.split('?');
    const params: Record<string, string> = {};

    if (queryString) {
        queryString.split('&').forEach(param => {
            const [key, value] = param.split('=');
            if (key) {
                params[decodeURIComponent(key)] = decodeURIComponent(value || '');
            }
        });
    }

    return {
        method,
        url: baseUrl,
        headers,
        body,
        params,
    };
}

/**
 * 将解析结果转换为 HttpRequest 对象
 * @param parsed 解析后的请求数据
 * @param name 请求名称
 * @param description 请求描述
 * @returns HttpRequest 对象
 */
export function toHttpRequest(
    parsed: ParsedRequest,
    name: string,
    description?: string
): Omit<HttpRequest, 'id' | 'created_at' | 'updated_at'> {
    return {
        name,
        description,
        method: parsed.method,
        url: parsed.url,
        headers: parsed.headers,
        body: parsed.body,
        params: parsed.params,
    };
}

/**
 * 验证解析结果
 * @param parsed 解析后的请求数据
 * @returns 验证结果
 */
export function validateParsedRequest(parsed: ParsedRequest): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!parsed.method) {
        errors.push('缺少 HTTP 方法');
    }

    if (!parsed.url) {
        errors.push('缺少请求 URL');
    } else {
        try {
            new URL(parsed.url);
        } catch {
            errors.push('URL 格式无效');
        }
    }

    return {
        valid: errors.length === 0,
        errors,
    };
} 