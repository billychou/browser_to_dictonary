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

# 短信验证码每日发送上限（同一手机号），防短信费用盗刷
CACHE_SMS_DAILY_PREFIX = "BCZ:SMS_SEND_DAILY"
CACHE_SMS_DAILY_TIMEOUT = 86400
SMS_DAILY_LIMIT = 10

# 添加词汇频控（同一用户每分钟上限），保存会联动词典外呼，防接口滥用
CACHE_WORD_ADD_PREFIX = "BCZ:WORD_ADD"
CACHE_WORD_ADD_TIMEOUT = 60
WORD_ADD_LIMIT_PER_MINUTE = 120

# 词典查询频控（同一用户每分钟上限），防外部词典 API 滥用
CACHE_DICT_LOOKUP_PREFIX = "BCZ:DICT_LOOKUP"
CACHE_DICT_LOOKUP_TIMEOUT = 60
DICT_LOOKUP_LIMIT_PER_MINUTE = 30
