local SCORE_RANK_ZSET_KEY = KEYS[1]
local SCORE_USER_HASH_KEY = KEYS[2]

local scores = redis.call('zrevrange', SCORE_RANK_ZSET_KEY, 0, -1)
if scores == nil then
    return nil
end

local rank = 1
local stats = {}
for _, s in pairs(scores) do
    local users = redis.call('hget', SCORE_USER_HASH_KEY, s)
    if users == nil then
        users = {}
    else
        users = cjson.decode(users)
    end

    local rankStatus = {rank, users}
    table.insert(stats, rankStatus)
    rank = rank + #users
end

if #stats == 0 then
    return nil
else
    return cjson.encode(stats)
end


