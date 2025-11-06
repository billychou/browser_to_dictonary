#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: sms_client.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
import sys
from typing import Optional, Dict

sys.path.append("/Users/songchuan.zhou/Src/browser_to_dictonary/vocabulary_book_backend/src/vocabulary_book_backend")

import logging
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredentialConfig
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from configs import app_config

logger = logging.getLogger(__name__)


class SmsClient:
    """
    短信服务
    """
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Dypnsapi20170525Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        print(app_config.ALIBABA_CLOUD_ACCESS_KEY_ID)
        print(app_config.ALIBABA_CLOUD_ACCESS_KEY_SECRET)
        credential_config = CredentialConfig(
            type='access_key',
            access_key_id=app_config.ALIBABA_CLOUD_ACCESS_KEY_ID,
            access_key_secret=app_config.ALIBABA_CLOUD_ACCESS_KEY_SECRET
        )
        credential = CredentialClient(credential_config)
        config = open_api_models.Config(
            credential=credential
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Dypnsapi
        config.endpoint = f'dypnsapi.aliyuncs.com'
        return Dypnsapi20170525Client(config)

    @staticmethod
    def send(code: str, phone: str) -> Optional[Dict]:
        """
        发送短信服务
        :param code:手机验证码
        :param phone:手机号码
        :return:
        """
        client = SmsClient.create_client()
        send_sms_verify_code_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            country_code="86",
            template_code="100001",
            scheme_name="登录/注册模板",
            template_param=f'{{"code":"{code}","min":"5"}}',
            sign_name="速通互联验证平台"
        )
        runtime = util_models.RuntimeOptions()
        try:
            ret = client.send_sms_verify_code_with_options(send_sms_verify_code_request, runtime)
            return ret
        except Exception as error:
            logger.error(error.message)
            raise Exception("发送短信验证码失败")
