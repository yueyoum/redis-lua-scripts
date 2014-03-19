# -*- coding: utf-8 -*-

import os
import hashlib
import json


SELF_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SELF_PATH, 'set.lua'), 'r') as f:
    SET_LUA = f.read()
    SET_LUA_HASH = hashlib.sha1(SET_LUA).hexdigest()

with open(os.path.join(SELF_PATH, 'query.lua'), 'r') as f:
    QUERY_LUA = f.read()
    QUERY_LUA_HASH = hashlib.sha1(QUERY_LUA).hexdigest()

with open(os.path.join(SELF_PATH, 'stats.lua'), 'r') as f:
    STATS_LUA = f.read()
    STATS_LUA_HASH = hashlib.sha1(STATS_LUA).hexdigest()


class ScoreRank(object):
    def __init__(self, r, USER_SCORE_HASH_KEY, SCORE_RANK_ZSET_KEY, SCORE_USER_HASH_KEY):
        # r is redis client instance
        self.r = r
        self.USER_SCORE_HASH_KEY = USER_SCORE_HASH_KEY
        self.SCORE_RANK_ZSET_KEY = SCORE_RANK_ZSET_KEY
        self.SCORE_USER_HASH_KEY = SCORE_USER_HASH_KEY

    def set(self, user_id, add_score):
        try:
            self.r.evalsha(SET_LUA_HASH, 3, self.USER_SCORE_HASH_KEY, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY, user_id, add_score)
        except Exception as e:
            print e
            self.r.eval(SET_LUA, 3, self.USER_SCORE_HASH_KEY, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY, user_id, add_score)

    def query(self, user_id):
        try:
            res = self.r.evalsha(QUERY_LUA_HASH, 3, self.USER_SCORE_HASH_KEY, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY, user_id)
        except Exception as e:
            print e
            res = self.r.eval(QUERY_LUA, 3, self.USER_SCORE_HASH_KEY, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY, user_id)

        if res:
            return json.loads(res)
        return res

    def stats(self):
        try:
            res = self.r.evalsha(STATS_LUA_HASH, 2, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY)
        except Exception as e:
            print e
            res = self.r.eval(STATS_LUA, 2, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY)

        if res:
            return json.loads(res)
        return res

    def get_score(self, user_id):
        score = self.r.get(self.USER_SCORE_HASH_KEY, user_id)
        return int(score) if score else None

    def clean(self):
        self.r.delete(self.USER_SCORE_HASH_KEY, self.SCORE_RANK_ZSET_KEY, self.SCORE_USER_HASH_KEY)
