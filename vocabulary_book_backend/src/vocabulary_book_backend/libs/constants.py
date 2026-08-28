#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: constants.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
# 短信验证码缓存键前缀
CACHE_SMS_CODE_PREFIX = "BCZ:SMS_CODE"
# 短信验证码缓存有效期300s
CACHE_SMS_CODE_TIMEOUT = 300
# 短信验证码错误次数缓存键前缀
CACHE_SMS_CODE_ERR_PREFIX = "BCZ:SMS_CODE_ERR"
# 同一验证码允许的最大错误次数，超过后需重新获取验证码
CACHE_SMS_CODE_ERR_MAX = 5

# 间隔复习（艾宾浩斯简化版）：等级对应的复习间隔天数
# 等级 0 为新词（立即复习），达到最高级视为已掌握
REVIEW_INTERVAL_DAYS = [0, 1, 2, 4, 7, 15]
# 已掌握的最低等级（即最高级索引）
REVIEW_MASTERED_STAGE = len(REVIEW_INTERVAL_DAYS) - 1
# 「模糊」结果的重新复习间隔（分钟）
REVIEW_FUZZY_DELAY_MINUTES = 10
