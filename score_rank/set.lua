-- 用来保存用户的积分 hash. key 为userid, value为 积分
local USER_SCORE_HASH_KEY = KEYS[1]
-- 用来查询某积分的排名 zset. value为 积分， score也为积分
local SCORE_RANK_ZSET_KEY = KEYS[2]
-- 用来查询相同积分的用户 hash. key 为积分，value为 json的userid列表
local SCORE_USER_HASH_KEY = KEYS[3]

local USER_ID = ARGV[1]
local USER_ADD_SCORE = ARGV[2]

USER_ADD_SCORE = tonumber(USER_ADD_SCORE)


local function contains(iterable, item)
    for a, b in pairs(iterable) do
        if b == item then
            return a
        end
    end
    return nil
end


local userOldScore = redis.call('hget', USER_SCORE_HASH_KEY, USER_ID)
local userNewScore = redis.call('hincrby', USER_SCORE_HASH_KEY, USER_ID, USER_ADD_SCORE)

redis.call('zadd', SCORE_RANK_ZSET_KEY, userNewScore, userNewScore)

if userOldScore ~= false then
    -- 这个用户设置过积分
    local oldScoreUsers = redis.call('hget', SCORE_USER_HASH_KEY, userOldScore)
    if oldScoreUsers ~= false then
        oldScoreUsers = cjson.decode(oldScoreUsers)
        local index = contains(oldScoreUsers, USER_ID)
        if index ~= nil then
            table.remove(oldScoreUsers, index)
        end

        if #oldScoreUsers == 0 then
            redis.call('hdel', SCORE_USER_HASH_KEY, userOldScore)
            redis.call('zrem', SCORE_RANK_ZSET_KEY, userOldScore)
        else
            redis.call('hset', SCORE_USER_HASH_KEY, userOldScore, cjson.encode(oldScoreUsers))
        end
    else
        redis.call('zrem', SCORE_RANK_ZSET_KEY, userOldScore)
    end
end

local newScoreUsers = redis.call('hget', SCORE_USER_HASH_KEY, userNewScore)
if newScoreUsers == false then
    redis.call('hset', SCORE_USER_HASH_KEY, userNewScore, cjson.encode({ USER_ID }))
else
    newScoreUsers = cjson.decode(newScoreUsers)
    local index = contains(newScoreUsers, USER_ID)
    if index == nil then
        table.insert(newScoreUsers, USER_ID)
        redis.call('hset', SCORE_USER_HASH_KEY, userNewScore, cjson.encode(newScoreUsers))
    end
end

return nil
