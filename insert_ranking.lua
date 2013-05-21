local rankListKey = KEYS[1]
local rankHashKey = KEYS[2]
local selfUid = ARGV[1]
local targetUid = ARGV[2]

local selfRank = redis.call('hget', rankHashKey, selfUid)
local targetRank = redis.call('hget', rankHashKey, targetUid)

selfRank = tonumber(selfRank)
targetRank = tonumber(targetRank)

if selfRank < targetRank then
    return 0
end

local uids = redis.call('lrange', rankListKey, targetRank-1, selfRank-2)

redis.call('lrem', rankListKey, 0, selfUid)
redis.call('linsert', rankListKey, 'before', targetUid, selfUid)

redis.call('hset', rankHashKey, selfUid, targetRank)
for _, uid in pairs(uids) do
    redis.call('hincrby', rankHashKey, uid, 1)
end

return #uids

