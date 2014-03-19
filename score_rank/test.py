import os

import redis

from scorerank import ScoreRank

REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

class Test(object):
    def setUp(self):
        self.r = redis.Redis(port=int(REDIS_PORT))

        self.sr = ScoreRank(self.r, 'a', 'b', 'c')
        data = [
            (1, 10),
            (2, 10),
            (3, 8),
            (4, 6),
            (5, 8),
            (6, 14),
            (7, 14),
            (8, 16)
        ]

        for user_id, add_score in data:
            self.sr.set(user_id, add_score)

    def tearDown(self):
        self.sr.clean()


    def _assert_list_equal(self, iterable, *args):
        assert len(iterable) == len(args)
        for a in args:
            assert a in iterable

    def _assert_query(self, userid, rank, *args):
        x = self.sr.query(userid)
        if rank is None:
            assert  x is None
        else:
            assert x['rank'] == rank
            self._assert_list_equal(x['users'], *args)

    def _assert_stats(self, expected_stats):
        stats = self.sr.stats()
        stats = dict(stats)
        assert len(stats) == len(expected_stats)
        for rank, users in expected_stats:
            self._assert_list_equal(stats[rank], *users)


    def test_a(self):
        self._assert_query(999, None)

        self._assert_query(8, 1, '8')

        self._assert_query(7, 2, '6', '7')
        self._assert_query(6, 2, '6', '7')

        self._assert_query(1, 4, '1', '2')
        self._assert_query(2, 4, '1', '2')

        self._assert_query(3, 6, '3', '5')
        self._assert_query(5, 6, '3', '5')

        self._assert_query(4, 8, '4')

        self._assert_stats([
            [1, ['8']], [2, ['6', '7']], [4, ['1', '2']], [6, ['3', '5']], [8, ['4']]
        ])

    def test_b(self):
        self.sr.set(4, 2)
        assert self.r.hget('a', 4) == '8'

        self._assert_query(8, 1, '8')

        self._assert_query(7, 2, '6', '7')
        self._assert_query(6, 2, '6', '7')

        self._assert_query(1, 4, '1', '2')
        self._assert_query(2, 4, '1', '2')

        self._assert_query(3, 6, '3', '5', '4')
        self._assert_query(4, 6, '3', '5', '4')
        self._assert_query(5, 6, '3', '5', '4')


        self._assert_stats([
            [1, ['8']], [2, ['6', '7']], [4, ['1', '2']], [6, ['3', '5', '4']]
        ])


    def test_c(self):
        self.sr.set(1, 2)
        assert self.r.hget('a', 1) == '12'

        self._assert_query(8, 1, '8')

        self._assert_query(7, 2, '6', '7')
        self._assert_query(6, 2, '6', '7')

        self._assert_query(1, 4, '1')
        self._assert_query(2, 5, '2')

        self._assert_query(3, 6, '3', '5')
        self._assert_query(5, 6, '3', '5')
        self._assert_query(4, 8, '4')

        self._assert_stats([
            [1, ['8']], [2, ['6', '7']], [4, ['1']], [5, ['2']], [6, ['3', '5']], [8, ['4']]
        ])



    def test_d(self):
        self.sr.set(6, 2)
        assert  self.r.hget('a', 6) == '16'

        self._assert_query(8, 1, '8', '6')
        self._assert_query(6, 1, '8', '6')

        self._assert_query(7, 3, '7')

        self._assert_query(1, 4, '1', '2')
        self._assert_query(2, 4, '1', '2')

        self._assert_query(3, 6, '3', '5')
        self._assert_query(5, 6, '3', '5')

        self._assert_query(4, 8, '4')

        self._assert_stats([
            [1, ['8', '6']], [3, ['7']], [4, ['1', '2']], [6, ['3', '5']], [8, ['4']]
        ])


