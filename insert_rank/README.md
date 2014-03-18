## insert_ranking.lua 插入排名

系统初始化有一个默认的排名：`A, B, C, D, E, F ...`

这些元素相互之间会PK，如果排名靠后的PK挑战排名靠前的，
并且胜利后，原先排在后面的元素就会插入到其PK对手的前面.
比如 E 挑战PK B，胜利后新的排序就是 `A, E, B, C, D, F ...`

这个排名系统需要响应多个用户发起的并发PK挑战，
并且能够实时的反映出每个人的名次变化。

使用 `insert_ranking.lua` 来完成PK名次的实时处理。在redis中需要两个key, 一个list，一个hash。

*   LISTKEY 用于内部保持排序

*   HASHKEY 用于取用户名次


#### 调用方式：

    r.eval(SCRIPT, 2, LISTKEY, HASHKEY, 发起挑战者id，被挑战者id)

#### 处理流程：

*   从hash key 中取两个用户的排名，如果发起挑战者排名本来就比被挑战者高，直接返回

*   发起挑战者的排名靠后，从LISTKEY中取出名次处于被挑战着和发起挑战着之间的用户id列表（包括被挑战着）。

*   将发起挑战者的id从LISTKEY中删除，并插入到被挑战者id的前面。并更新HASHKEY中此用户的排名。这完成了挑战者自身的名次变化

*   将第二步得到的用户列表，依次更新其在HASHKEY中的排名。（其实就是+1）。这完成了因为后面有人插入到前面，导致的中间所有人名次后移的变化

#### test:

    python insert_ranking_test.py


