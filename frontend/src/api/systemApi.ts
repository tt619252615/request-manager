/**
 * 系统管理API
 */
import { client } from './client';

export interface NetworkTimeInfo {
    network_time: string;
    timestamp: number;
    time_diff: number;
    formatted_time: string;
}

export interface TimeSyncResult {
    time_diff: number;
    network_time: string;
    sync_success: boolean;
}

export const systemApi = {
    /**
     * 获取当前网络时间
     */
    async getNetworkTime(): Promise<NetworkTimeInfo> {
        return await client.get<NetworkTimeInfo>('/system/network-time');
    },

    /**
     * 手动同步网络时间
     */
    async syncNetworkTime(): Promise<TimeSyncResult> {
        return await client.post<TimeSyncResult>('/system/sync-time');
    },
}; 