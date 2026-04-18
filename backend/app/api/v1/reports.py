"""
高级报表 API 接口
提供多维度数据分析和报表生成接口
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ..services.report import generate_full_report, ReportDataGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["报表管理"])


# ==================== 响应模型 ====================

class ReportResponse(BaseModel):
    """报表响应"""
    code: int = 0
    msg: str = "success"
    data: Optional[Dict[str, Any]] = None


# ==================== 报表接口 ====================

@router.get("/overview", summary="项目概览报表")
async def get_overview_report():
    """获取项目概览报表"""
    try:
        report = generate_full_report("overview")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成概览报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend", summary="任务趋势报表")
async def get_trend_report(days: int = Query(30, ge=7, le=90)):
    """获取任务趋势报表"""
    try:
        generator = ReportDataGenerator()
        trend_data = generator.get_task_trend(days)
        return ReportResponse(data={
            "generated_at": datetime.now().isoformat(),
            "report_type": "任务趋势报表",
            "period_days": days,
            "data": {
                "trend": trend_data
            }
        })
    except Exception as e:
        logger.error(f"生成趋势报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team", summary="团队绩效报表")
async def get_team_report():
    """获取团队绩效报表"""
    try:
        report = generate_full_report("team")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成团队报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource", summary="资源利用报表")
async def get_resource_report():
    """获取资源利用报表"""
    try:
        report = generate_full_report("resource")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成资源报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget", summary="预算分析报表")
async def get_budget_report():
    """获取预算分析报表"""
    try:
        report = generate_full_report("budget")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成预算报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk", summary="风险分析报表")
async def get_risk_report():
    """获取风险分析报表"""
    try:
        report = generate_full_report("risk")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成风险报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comprehensive", summary="综合报表")
async def get_comprehensive_report():
    """获取综合报表（包含所有维度）"""
    try:
        report = generate_full_report("comprehensive")
        return ReportResponse(data=report)
    except Exception as e:
        logger.error(f"生成综合报表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", summary="仪表盘数据")
async def get_dashboard_data():
    """获取仪表盘数据（精简版）"""
    try:
        generator = ReportDataGenerator()
        
        # 概览数据
        overview = generator.get_project_overview()
        
        # 趋势数据（最近7天）
        trend = generator.get_task_trend(7)
        
        # 团队绩效（前5名）
        team = generator.get_team_performance()[:5]
        
        # 资源利用
        resource = generator.get_resource_utilization()
        
        return ReportResponse(data={
            "generated_at": datetime.now().isoformat(),
            "summary": overview["summary"],
            "projects": overview["projects"],
            "team": overview["team"],
            "trend": trend[-7:],
            "top_performers": team,
            "resource_utilization": resource["overall"],
            "budget": {
                "total": generator.get_budget_analysis()["total_budget"],
                "spent": generator.get_budget_analysis()["spent"],
                "remaining": generator.get_budget_analysis()["remaining"]
            },
            "risk_count": len(generator.get_risk_analysis())
        })
    except Exception as e:
        logger.error(f"生成仪表盘数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 报表列表 ====================

@router.get("/types", summary="报表类型列表")
async def get_report_types():
    """获取所有可用的报表类型"""
    return ReportResponse(data={
        "types": [
            {"id": "overview", "name": "项目概览", "description": "项目整体状态和进度"},
            {"id": "trend", "name": "任务趋势", "description": "任务创建和完成趋势"},
            {"id": "team", "name": "团队绩效", "description": "团队成员工作绩效"},
            {"id": "resource", "name": "资源利用", "description": "资源使用情况分析"},
            {"id": "budget", "name": "预算分析", "description": "预算执行情况"},
            {"id": "risk", "name": "风险分析", "description": "项目风险评估"},
            {"id": "comprehensive", "name": "综合报表", "description": "所有报表汇总"},
            {"id": "dashboard", "name": "仪表盘", "description": "精简仪表盘数据"}
        ]
    })