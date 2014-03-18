import sys
from optparse import OptionParser

import redis

parse = OptionParser()
parse.add_option(
    '-p', '--port',
    type = 'int',
    dest = 'port',
    default = 6379,
)


options, args = parse.parse_args(sys.argv)

r = redis.Redis(port=options.port)

with open('insert_ranking.lua', 'r') as f:
    x = f.read()


RANK_LIST_KEY = 'testl'
RANK_HASH_KEY = 'testh'


r.delete(RANK_LIST_KEY)
r.delete(RANK_HASH_KEY)

pipe = r.pipeline()
uids = xrange(1, 10001)

for index, uid in enumerate(uids):
    pipe.rpush(RANK_LIST_KEY, uid)
    pipe.hset(RANK_HASH_KEY, uid, index+1)

pipe.execute()


def test(*args):
    for uid, rank in zip(args[::2], args[1::2]):
        assert int( r.hget(RANK_HASH_KEY, uid) ) == rank


test(1, 1, 1000, 1000, 10000, 10000)

r.eval(x, 2, RANK_LIST_KEY, RANK_HASH_KEY, 1000, 1)
test(1, 2, 1000, 1, 990, 991, 1001, 1001)

r.eval(x, 2, RANK_LIST_KEY, RANK_HASH_KEY, 9000, 1000)
test(1, 3, 1000, 2, 9000, 1, 990, 992, 1001, 1002, 10000, 10000)

r.eval(x, 2, RANK_LIST_KEY, RANK_HASH_KEY, 10000, 1)
test(1, 4, 1000, 2, 990, 993, 10000, 3)


r.delete(RANK_LIST_KEY)
r.delete(RANK_HASH_KEY)

