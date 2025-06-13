"""
系统管理 API
"""

from fastapi import APIRouter
from ..schemas.response import BaseResponse, success_response, error_response, ErrorCodes
from ..services.network_time_service import network_time_service

# 创建路由器
router = APIRouter()


@router.get("/network-time", response_model=BaseResponse[dict])
async def get_network_time():
    """获取当前网络时间"""
    try:
        current_time = network_time_service.get_current_network_time()
        time_diff = network_time_service.get_time_diff()
        
        data = {
            "network_time": network_time_service.format_time_with_ms(current_time),
            "timestamp": int(current_time.timestamp() * 1000),  # 毫秒时间戳
            "time_diff": round(time_diff, 3),  # 时间差（秒）
            "formatted_time": current_time.strftime('%H:%M:%S.%f')[:-3]  # 只显示时间部分
        }
        
        return success_response(data=data, message="获取网络时间成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取网络时间失败: {str(e)}"
        )


@router.post("/sync-time", response_model=BaseResponse[dict])
async def sync_network_time():
    """手动同步网络时间"""
    try:
        time_diff = network_time_service.sync_time_diff()
        current_time = network_time_service.get_current_network_time()
        
        if time_diff is not None:
            data = {
                "time_diff": round(time_diff, 3),
                "network_time": network_time_service.format_time_with_ms(current_time),
                "sync_success": True
            }
            return success_response(data=data, message="网络时间同步成功")
        else:
            return error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="网络时间同步失败"
            )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"网络时间同步失败: {str(e)}"
        ) 