#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
词典客户端（Free Dictionary API，英文词）

File: dictionary_client.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from configs import app_config

logger = logging.getLogger(__name__)

# 归一化时的截断上限，避免超大响应直接落库
_MAX_MEANINGS = 5
_MAX_DEFS_PER_MEANING = 3


class DictionaryClient:
    """
    词典查询，输出归一化结构：
    {
        "phonetic": "/həˈləʊ/",
        "definition": "exclamation. Used to express a greeting...",
        "detail": [{"pos": "exclamation", "definitions": [{"definition": "...", "example": "..."}]}]
    }
    """

    @staticmethod
    def lookup(word: str) -> Optional[Dict[str, Any]]:
        """
        查询单词释义。
        :param word: 单词
        :return: 归一化释义；词典无收录时返回 None；网络/接口异常抛出异常
        """
        base = app_config.DICTIONARY_API_BASE
        if not base or not word or not word.strip():
            return None
        url = f"{base.rstrip('/')}/{quote(word.strip())}"
        response = requests.get(url, timeout=app_config.DICTIONARY_TIMEOUT)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        entries = response.json()
        if not isinstance(entries, list) or not entries:
            return None
        return DictionaryClient.normalize(entries)

    @staticmethod
    def normalize(entries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """将词典 API 的原始条目归一化为统一结构"""
        phonetic = ""
        detail: List[Dict[str, Any]] = []
        for entry in entries:
            if not phonetic:
                phonetic = entry.get("phonetic") or ""
                if not phonetic:
                    for p in entry.get("phonetics") or []:
                        if p.get("text"):
                            phonetic = p["text"]
                            break
            for meaning in (entry.get("meanings") or [])[:_MAX_MEANINGS]:
                pos = meaning.get("partOfSpeech") or ""
                defs = []
                for d in (meaning.get("definitions") or [])[:_MAX_DEFS_PER_MEANING]:
                    text = (d.get("definition") or "").strip()
                    if not text:
                        continue
                    item: Dict[str, str] = {"definition": text}
                    if d.get("example"):
                        item["example"] = d["example"]
                    defs.append(item)
                if defs:
                    detail.append({"pos": pos, "definitions": defs})
        if not detail:
            return None
        definition = "\n".join(
            f"{d['pos']}. {d['definitions'][0]['definition']}"
            if d["pos"]
            else d["definitions"][0]["definition"]
            for d in detail
        )
        return {"phonetic": phonetic, "definition": definition, "detail": detail}
