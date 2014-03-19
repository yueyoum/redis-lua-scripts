import os
import random
import redis

from scorerank import  ScoreRank

REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

class BenchMark(object):
    def __init__(self, data):
        self.r = redis.Redis(port=int(REDIS_PORT))
        self.sr = ScoreRank(self.r, 'a', 'b', 'c')

        self.all_userids = []

        for userid, score in data:
            self.all_userids.append(userid)
            self.sr.set(userid, score)
        print "start"


    def random_set(self):
        userid = random.choice(self.all_userids)
        add_score = random.randint(1, 999)
        self.sr.set(userid, add_score)

    def random_query(self):
        userid = random.choice(self.all_userids)
        self.sr.query(userid)

    def stats(self):
        self.sr.stats()

    def clean(self):
        self.sr.clean()


if __name__ == '__main__':
    from timeit import Timer

    data = []
    for i in range(100000):
        userid = i + 1
        data.append((userid, random.randint(1, 100000)))

    b = BenchMark(data)

    t1 = Timer("b.random_set()", "from __main__ import b")
    print t1.timeit(10000)

    t2 = Timer("b.random_query()", "from __main__ import b")
    print t2.timeit(100)

    t3 = Timer("b.stats()", "from __main__ import b")
    print t3.timeit(1)

    b.clean()


