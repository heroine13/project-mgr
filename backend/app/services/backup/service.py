"""
Backup Service - Database backup and restore functionality
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import sqlite3

class BackupService:
    """Service for database backup and restore"""
    
    def __init__(self, db_path: str, backup_dir: str = "./backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, name: Optional[str] = None) -> Dict:
        """Create a database backup"""
        if not name:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = self.backup_dir / f"{name}.db"
        backup_info = self.backup_dir / f"{name}.json"
        
        # Copy database file
        shutil.copy2(self.db_path, backup_file)
        
        # Calculate checksum
        checksum = self._calculate_checksum(backup_file)
        
        # Get database info
        db_info = self._get_db_info(backup_file)
        
        # Create metadata
        metadata = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "file_size": backup_file.stat().st_size,
            "checksum": checksum,
            "tables": db_info["tables"],
            "total_records": db_info["total_records"]
        }
        
        # Save metadata
        with open(backup_info, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata
    
    def restore_backup(self, name: str) -> Dict:
        """Restore database from backup"""
        backup_file = self.backup_dir / f"{name}.db"
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {name}")
        
        # Verify checksum
        metadata = self.get_backup_info(name)
        current_checksum = self._calculate_checksum(backup_file)
        
        if current_checksum != metadata.get("checksum"):
            raise ValueError("Backup file integrity check failed")
        
        # Create backup of current database before restore
        current_backup = f"{self.db_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.db_path, current_backup)
        
        # Restore
        shutil.copy2(backup_file, self.db_path)
        
        return {
            "status": "success",
            "restored_from": name,
            "pre_restore_backup": current_backup,
            "restored_at": datetime.now().isoformat()
        }
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for info_file in self.backup_dir.glob("*.json"):
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    backups.append(metadata)
            except Exception:
                continue
        
        # Sort by creation date, newest first
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    def get_backup_info(self, name: str) -> Optional[Dict]:
        """Get backup metadata"""
        info_file = self.backup_dir / f"{name}.json"
        
        if not info_file.exists():
            return None
        
        with open(info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_backup(self, name: str) -> bool:
        """Delete a backup"""
        backup_file = self.backup_dir / f"{name}.db"
        info_file = self.backup_dir / f"{name}.json"
        
        deleted = False
        
        if backup_file.exists():
            backup_file.unlink()
            deleted = True
        
        if info_file.exists():
            info_file.unlink()
            deleted = True
        
        return deleted
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def _get_db_info(self, db_path: Path) -> Dict:
        """Get database information"""
        info = {"tables": {}, "total_records": 0}
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Skip system tables
                if table.startswith('sqlite_'):
                    continue
                
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    info["tables"][table] = count
                    info["total_records"] += count
                except Exception:
                    continue
            
            conn.close()
        
        except Exception:
            pass
        
        return info


# Singleton instance - will be initialized with actual db path
_backup_service: Optional[BackupService] = None

def get_backup_service(db_path: str = None, backup_dir: str = None) -> BackupService:
    """Get or create backup service instance"""
    global _backup_service
    
    if _backup_service is None:
        # Default paths
        if db_path is None:
            # Try to get from environment or use default
            db_path = os.environ.get("DATABASE_URL", "./data/project_manager.db")
            if db_path.startswith("sqlite:///"):
                db_path = db_path.replace("sqlite:///", "")
        
        if backup_dir is None:
            backup_dir = "./backups"
        
        _backup_service = BackupService(db_path, backup_dir)
    
    return _backup_service