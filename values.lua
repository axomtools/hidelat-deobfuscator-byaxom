local V = {}
function V.lit(c) return {code = c} end
function V.const(v)
  if type(v) == "string" then return {code = string.format("%q", v), raw = v} end
  if type(v) == "number" then return {code = tostring(v), raw = v} end
  if type(v) == "boolean" then return {code = v and "true" or "false", raw = v} end
  return {code = tostring(v)}
end
function V.global(n) return {code = n, raw = n, g = true} end
function V.expr(c) return {code = c} end

local cv = function(v)
  if type(v) == "table" then return v.code or "vnil" end
  if v == nil then return "vnil" end
  return tostring(v)
end
local rv = function(v) return type(v) == "table" and v.raw or nil end
local isident = function(s) return type(s) == "string" and s:match("^[%a_][%w_]*$") end

local function idxaccess(obj, idxv)
  local oc = cv(obj)
  local kr = rv(idxv)
  if type(kr) == "string" then
    if isident(kr) then return V.expr(oc.."."..kr) end
    return V.expr(oc.."["..string.format("%q", kr).."]")
  end
  if type(kr) == "number" then return V.expr(oc.."["..kr.."]") end
  return V.expr(oc.."["..cv(idxv).."]")
end

local function fmtval(v)
  if v == nil then return "nil" end
  if type(v) == "string" then return string.format("%q", v) end
  return tostring(v)
end

return {
  V = V,
  cv = cv,
  rv = rv,
  isident = isident,
  idxaccess = idxaccess,
  fmtval = fmtval
}
