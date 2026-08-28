#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""

from flask import g
from flask_restful import Resource
from flask_restful import marshal
from flask_restful import reqparse

from fields.words_fields import word_list_resp_fields
from fields.words_fields import word_post_resp_fields
from libs.auth import jwt_required
from services.vocabulary_service import VocabularyService


class WordResource(Resource):
    """
    单词集合接口（需登录，数据归属当前用户）
    """

    @jwt_required
    def get(self):
        """
        分页查询当前用户的词汇列表
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("word", type=str, required=False, location="args")
        parser.add_argument("page", type=int, required=False, default=1, location="args")
        parser.add_argument("limit", type=int, required=False, default=50, location="args")
        args = parser.parse_args()

        uid = str(g.current_user.id)
        words, total = VocabularyService.list_by_user(
            uid=uid, word=args["word"], page=args["page"], limit=args["limit"]
        )
        return marshal(
            dict(
                success=True,
                message="success",
                data=dict(
                    total=total,
                    page=max(args["page"], 1),
                    limit=args["limit"],
                    items=words,
                ),
            ),
            word_list_resp_fields,
        )

    @jwt_required
    def post(self):
        """
        保存单词，归属当前登录用户，按 (uid, word) 去重
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("word", type=str, required=True, location="json")
        args = parser.parse_args()
        data = VocabularyService.add(uid=str(g.current_user.id), word=args["word"])
        return marshal(
            dict(success=True, message="success", data=data), word_post_resp_fields
        )


class WordItemResource(Resource):
    """
    单个单词接口（需登录，仅允许操作本人词汇）
    """

    @jwt_required
    def put(self, word_id: int):
        """
        更新单词内容
        :param word_id: 词汇记录ID
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("word", type=str, required=True, location="json")
        args = parser.parse_args()
        try:
            data = VocabularyService.update_owned(
                uid=str(g.current_user.id), word_id=word_id, word_text=args["word"]
            )
        except Exception as e:
            return dict(success=False, message=str(e), data=None), 400
        return marshal(
            dict(success=True, message="success", data=data), word_post_resp_fields
        )

    @jwt_required
    def delete(self, word_id: int):
        """
        删除单词
        :param word_id: 词汇记录ID
        :return:
        """
        try:
            VocabularyService.delete_owned(uid=str(g.current_user.id), word_id=word_id)
        except Exception as e:
            return dict(success=False, message=str(e), data=None), 400
        return dict(success=True, message="success", data=None)


class WordDefinitionResource(Resource):
    """
    单词释义补查接口（需登录，仅允许操作本人词汇）
    """

    @jwt_required
    def put(self, word_id: int):
        """
        重新查询词典释义（首次保存查询失败时可补查）
        :param word_id: 词汇记录ID
        :return:
        """
        try:
            data = VocabularyService.refresh_definition_owned(
                uid=str(g.current_user.id), word_id=word_id
            )
        except Exception as e:
            return dict(success=False, message=str(e), data=None), 400
        return marshal(
            dict(success=True, message="success", data=data), word_post_resp_fields
        )


class WordReviewResource(Resource):
    """
    单词复习接口（需登录，仅允许操作本人词汇）
    """

    @jwt_required
    def put(self, word_id: int):
        """
        记录一次复习结果（known | fuzzy | unknown），服务端统一计算排期
        :param word_id: 词汇记录ID
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("result", type=str, required=True, location="json")
        args = parser.parse_args()
        try:
            data = VocabularyService.review_owned(
                uid=str(g.current_user.id), word_id=word_id, result=args["result"]
            )
        except Exception as e:
            return dict(success=False, message=str(e), data=None), 400
        return marshal(
            dict(success=True, message="success", data=data), word_post_resp_fields
        )
