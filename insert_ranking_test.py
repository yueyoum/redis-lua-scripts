import redis
r = redis.Redis(port=6381)

with open('update_arean_rank.lua', 'r') as f:
    x = f.read()

r.delete('aabb')
r.delete('aahh')

pipe = r.pipeline()
uids = xrange(1, 10001)

for index, uid in enumerate(uids):
    pipe.rpush('aabb', uid)
    pipe.hset('aahh', uid, index+1)

pipe.execute()


def test(*args):
    for uid, rank in zip(args[::2], args[1::2]):
        assert int( r.hget('aahh', uid) ) == rank

print 'start test'

test(1, 1, 1000, 1000)

r.eval(x, 2, 'aabb', 'aahh', 1000, 1)
test(1, 2, 1000, 1, 990, 991, 1001, 1001)

r.eval(x, 2, 'aabb', 'aahh', 9000, 1000)
test(1, 3, 1000, 2, 9000, 1, 990, 992, 1001, 1002, 10000, 10000)

r.eval(x, 2, 'aabb', 'aahh', 10000, 1)
test(1, 4, 1000, 2, 990, 993, 10000, 3)

print r.lrange('aabb', 0, 10)

r.delete('aabb')
r.delete('aahh')

