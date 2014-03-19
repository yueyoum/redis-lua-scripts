# score ranking 积分排名

通过3个key，在redis中存取数据

1.  USER_SCORE_HASH_KEY
2.  SCORE_RANK_ZSET_KEY
3.  SCORE_USER_HASH_KEY


#### USER_SCORE_HASH_KEY

key 为userid, value 为积分. 用来保存用户积分

#### SCORE_RANK_ZSET_KEY

 value 为积分，score也是此积分. 用来查询排在某积分前面的积分

#### SCORE_USER_HASH_KEY

key 为积分，value为 json encode后的 userid列表.  用来统计某积分有多少用户


## 处理流程

首先需要自定义上面的三个key，举例为 'a', 'b', 'c'

#### set.lua

当某用户要增加积分，调用此脚本

    redis.eval(SET_LUA, 3, 'a', 'b', 'c', userId, add_score)

返回nil

#### query.lua

要查询某人的排名，调用此脚本

    redis.eval(QUERY_LUA, 3, 'a', 'b', 'c', userId)

**NOTE** 实时查询排名比较耗时。所以最好是定时用stats.lua得到所有人的排名，然后将其缓存。

如果没有此人排名，返回nil
否则返回 可以json 反序列化的字符串。 反序列化后为

    {
        'rank': RANK_NUMBER,
        'users': [USERID, USERID]
    }


其中 rank 为此用户积分对应的最高排名，users为与userId具有相同积分的用户列表。（包括userId）

这样，就可以再根据user的其他属性对 这些users进一步排序。

伪代码：

    uid_and_other_property = get_other_property(users)
    # [[uid, p1], [uid, p2]...]
    users = sort_by_other_property(uid_and_other_property)
    # 排序后的users

    for index, user in enumerate(users):
        user.rank = RANK_NUMBER + index


_此用户积分对应的最高排名是什么意思？_

举例： 有四个用户 A， B， C，D  积分分别为 10, 10, 8, 8

则，A， B 查询到的 rank 也就是积分对应最高排名是 1
而  C,  D 对应的rank则是 3




#### stats.lua

得到所有人的排名

    redis.eval(STATS_LUA, 2, 'b', 'c')

如果没有任何人的排名，返回nil
否则返回可以json反序列化的字符串， 反序列化后为

    [
        [RANK_NUMBER, [USERID, USERID...]],
        [RANK_NUMBER, [USERID, USERID...]],
        ...
    ]


这个列表是按照 rank 排名，从第一名往后排的。

所以要得到每个人的排名，其伪代码为:

    for rank, users in RESULT:
        users = sort_by_other_property(users)
        for index, u in enumerate(users):
            print rank, u


**NOTE** 取所有人排名是个比较轻量级的操作，所以建议按照实际需求，每隔一段时间就取所人的排名，然后将其缓存起来。
查询某人的排名，就直接从这个缓存里取。而不是用上面的query.lua。 这样系统负担就小的多。



## 原理

#### 插入

用户a要增加1积分，

1.  查询a的原始积分。然后给a增加积分。
2.  将新积分 zadd 到 SCORE_RANK_ZSET_KEY
3.  按照新积分为key，将a加入到 SCORE_USER_HASH_KEY value 列表中
4.  将 SCORE_USER_HASH_KEY 原始积分的value列表中去除a
5.  如果去除后 value为空，则从 SCORE_USER_HASH_KEY 和 SCORE_RANK_ZSET_KEY 删掉原始积分


#### 查询

1.  从 USER_SCORE_HASH_KEY 中查询a的积分
2.  如果没有，则返回nil
3.  如果有积分，首先通过 SCORE_RANK_ZSET_KEY 得到a积分前面还有多少积分
4.  从 SCORE_USER_HASH_KEY 一一遍历 比a积分大的积分用户数量，将其累加。就得到a积分的最高排名
5.  从 SCORE_USER_HASH_KEY 得到和a积分有一样积分的用户列表
6.  将最高排名和用户列表返回


## Test

直接运行 `nosetests`

如果你的redis不在默认的 6379 端口，则这样运行

    REDIS_PORT=YOUR_PORT nosetests


## BenchMark

你可以修改参数，或者直接运行

    python benchmark.py

1万用户的benchmark输出：

    3.9942138195
    1.47855710983
    0.0559611320496

10万用户的benchmark输出：

    4.21314311028
    15.4578120708
    0.507577896118

默认设定为： 有1万用户参与积分排名，

*   1万次set积分，耗时4s
*   100次对单个用户的实时排名查询，耗时1.5s
*   将一万用户的排名全部取一次，耗时0.05s


从测试数据可以看出以下几点注意：

1.  实时查询性能很差，尽量避免。解决办法就是上面说的，用stats.lua获取全部排名，处理后缓存起来。然后从缓存中获取排名
2.  用户基数对插入的影响不大，但对查询有很大影响。如果用户基数很少，再测试确认后，也可以用实时查询。








