"""
Backup API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.backup.service import get_backup_service

router = APIRouter(prefix="/backup", tags=["备份管理"])


def get_backup_svc():
    """Get backup service instance"""
    # Get database path from config
    from app.core.config import settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "") if hasattr(settings, 'DATABASE_URL') else "./data/project_manager.db"
    backup_dir = "./backups"
    return get_backup_service(db_path, backup_dir)


@router.get("/list")
async def list_backups(
    current_user: User = Depends(get_current_user)
):
    """List all available backups"""
    # Only admin can list backups
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以查看备份列表")
    
    backup_service = get_backup_svc()
    backups = backup_service.list_backups()
    
    return {
        "backups": backups,
        "total": len(backups)
    }


@router.post("/create")
async def create_backup(
    name: str = None,
    current_user: User = Depends(get_current_user)
):
    """Create a new database backup"""
    # Only admin can create backups
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以创建备份")
    
    backup_service = get_backup_svc()
    
    try:
        metadata = backup_service.create_backup(name)
        return {
            "status": "success",
            "message": "备份创建成功",
            "backup": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份创建失败: {str(e)}")


@router.post("/restore/{backup_name}")
async def restore_backup(
    backup_name: str,
    current_user: User = Depends(get_current_user)
):
    """Restore database from backup"""
    # Only admin can restore
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以恢复备份")
    
    backup_service = get_backup_svc()
    
    try:
        result = backup_service.restore_backup(backup_name)
        return {
            "status": "success",
            "message": "数据库恢复成功",
            "details": result
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@router.delete("/{backup_name}")
async def delete_backup(
    backup_name: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a backup"""
    # Only admin can delete backups
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以删除备份")
    
    backup_service = get_backup_svc()
    
    try:
        success = backup_service.delete_backup(backup_name)
        if success:
            return {"status": "success", "message": f"备份 {backup_name} 已删除"}
        else:
            raise HTTPException(status_code=404, detail="备份文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/download/{backup_name}")
async def download_backup(
    backup_name: str,
    current_user: User = Depends(get_current_user)
):
    """Download a backup file"""
    # Only admin can download
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以下载备份")
    
    backup_service = get_backup_svc()
    backup_file = backup_service.backup_dir / f"{backup_name}.db"
    
    if not backup_file.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")
    
    return FileResponse(
        path=str(backup_file),
        filename=f"{backup_name}.db",
        media_type="application/octet-stream"
    )


@router.post("/upload")
async def upload_backup(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and restore a backup file"""
    # Only admin can upload
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以上传备份")
    
    backup_service = get_backup_svc()
    
    # Save uploaded file
    temp_path = backup_service.backup_dir / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Verify it's a valid SQLite database
        import sqlite3
        conn = sqlite3.connect(temp_path)
        conn.close()
        
        # Get backup name from filename
        backup_name = file.filename.replace(".db", "")
        
        # Move to backup directory
        final_path = backup_service.backup_dir / f"{backup_name}.db"
        temp_path.rename(final_path)
        
        return {
            "status": "success",
            "message": f"备份文件 {backup_name} 上传成功",
            "backup_name": backup_name
        }
        
    except Exception as e:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=400, detail=f"上传失败: {str(e)}")