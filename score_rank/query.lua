local USER_SCORE_HASH_KEY = KEYS[1]
local SCORE_RANK_ZSET_KEY = KEYS[2]
local SCORE_USER_HASH_KEY = KEYS[3]

local USER_ID = ARGV[1]

local userScore = redis.call('hget', USER_SCORE_HASH_KEY, USER_ID)
if userScore == false then
    return nil
end

userScore = tonumber(userScore)

local ranks = redis.call('zrevrangebyscore', SCORE_RANK_ZSET_KEY, '+inf', '(' .. userScore)

local realRank = 0
for _, r in pairs(ranks) do
    local thisRankUsers = redis.call('hget', SCORE_USER_HASH_KEY, r)
    if thisRankUsers ~= nil then
        thisRankUsers = cjson.decode(thisRankUsers)
        realRank = realRank + #thisRankUsers
    end
end

realRank = realRank + 1

local sameScoreUsers = redis.call('hget', SCORE_USER_HASH_KEY, userScore)
local result = {rank=realRank, users=cjson.decode(sameScoreUsers)}

return cjson.encode(result)
