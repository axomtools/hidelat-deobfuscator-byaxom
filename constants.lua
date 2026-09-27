local mod32 = 4294967296
local mod16 = 65536
local lcg = function(s) return (s*1664525+1013904223)%mod32 end
local pesc = function(s) return (s:gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])","%%%1")) end
local pf = function(b,s) return b:find(s,1,true)~=nil end
local regpat = function(r,i) return pesc(r).."%["..pesc(i).."%]" end
local regplus = function(r,b,o) return pesc(r).."%["..pesc(b.."+"..o).."%]" end
return {
  mod32 = mod32,
  mod16 = mod16,
  lcg = lcg,
  pesc = pesc,
  pf = pf,
  regpat = regpat,
  regplus = regplus
}
