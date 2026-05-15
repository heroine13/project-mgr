"""
AI Service - 智能项目管理功能 (增强版)
支持: OpenAI GPT, Anthropic Claude, 本地模型
配置从数据库读取，修改后自动刷新
"""

import json
import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# 配置缓存
_ai_config_cache = None  # dict 或 None
_ai_config_cache_key = None  # (provider_name, 版本号)
_openai_client = None
_anthropic_client = None
