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
