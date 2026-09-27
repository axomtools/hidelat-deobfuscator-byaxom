local constants = require("constants")
local values = require("values")
local mod32 = constants.mod32
local lcg = constants.lcg
local V = values.V
local cv = values.cv
local rv = values.rv
local isident = values.isident
local idxaccess = values.idxaccess

local function decode(proto, info, opmap, decoder)
  local fds, an, bn, cn = info.fields, info.an, info.bn, info.cn
  local kp = proto[4]
  local cache, consts = {}, {}
  for i = 1, #kp do
    local ok, v = pcall(decoder, kp, cache, i)
    if ok then consts[i] = v end
  end
  local code = {}
  for ip = 1, #proto[3] do
    local raw = proto[3][ip]
    local s = (proto[8] + ip * 65599) % mod32
    local v = {}
    for _, fd in ipairs(fds) do
      s = lcg(s)
      v[fd.name] = (raw[fd.idx] - s) % fd.mod
    end
    code[ip] = {
      op = opmap[v[fds[1].name]],
      A = v[an],
      B = v[bn],
      C = v[cn]
    }
  end
  return code, consts, proto[5] or {},
    {nparam = proto[1] or 0, isvarag = (proto[2] or 0) % 2, nups = #(proto[6] or {})}
end

local function dec(code, consts, plist, pmeta, info, opmap, decoder, opn, indent, main, opts)
  indent = indent or ""
  main = main == nil and true or main
  opts = opts or {}
  local cf = opts.cf and true or false
  local n = #code
  local r = {}
  local out = {}
  local ip = 1
  local function emit(s) table.insert(out, indent..s) end
  local npinit = main and 0 or pmeta.nparam
  for i = 0, npinit - 1 do r[i] = V.lit("v"..i) end
  local usedups = {}
  for ii = 1, n do
    local ins = code[ii]
    local o = opn[ins.op]
    if o == "GETUPVAL" or o == "SETUPVAL" then usedups[ins.B] = true end
  end
  local updecls = {}
  for ub in pairs(usedups) do
    table.insert(updecls, "v"..string.format("%02d", ub))
  end
  table.sort(updecls)
  if #updecls > 0 then emit("local "..table.concat(updecls, ", ")) end
  emit("local vnil = nil")
  local function findselfbefore(ci, aa)
    local j = ci - 1
    while j >= 1 do
      local pi = code[j]
      if not pi then break end
      local pop = opn[pi.op]
      if pop == "JUNK" or pop == "LOADK" or pop == "MOVE" or pop == "LOADNIL" or
        pop == "LOADBOOL" or pop == "CLOSURE" or pop == "GETUPVAL" or pop == "SETUPVAL" or
        pop == "GETTABLE" or pop == "NEWTABLE" or pop == "NEWTABLE1" then
        j = j - 1
      elseif pop == "SELF" and pi.A == aa then
        return j
      else
        break
      end
    end
  end
  while ip <= n do
    local ins = code[ip]
    local op = opn[ins.op]
    local aa, bb, cc = ins.A, ins.B, ins.C
    if op == "JUNK" or op == "JMP" then
    elseif op == "LOADK" then
      local v = consts[bb+1]
      if v == nil then r[aa] = V.lit("nil")
      elseif type(v) == "string" then r[aa] = V.const(v)
      elseif type(v) == "number" then r[aa] = V.const(v)
      elseif type(v) == "boolean" then r[aa] = V.const(v)
      else r[aa] = V.lit(tostring(v)) end
    elseif op == "GETGLOBAL" then
      r[aa] = V.global(tostring(consts[bb+1]))
    elseif op == "SETGLOBAL" then
      emit(tostring(consts[bb+1]).." = "..cv(r[aa]))
    elseif op == "MOVE" then
      r[aa] = r[bb]
    elseif op == "NOT" then
      r[aa] = V.expr("(not "..cv(r[bb])..")")
    elseif op == "UNM" then
      r[aa] = V.expr("-"..cv(r[bb]))
    elseif op == "LEN" then
      r[aa] = V.expr("#"..cv(r[bb]))
    elseif op == "NEWTABLE" then
      r[aa] = V.lit("{}")
    elseif op == "NEWTABLE1" then
      r[aa] = V.expr("{"..cv(r[bb]).."}")
    elseif op == "LOADNIL" then
      for i = 0, bb do r[aa+i] = V.lit("nil") end
    elseif op == "LOADBOOL" then
      r[aa] = V.const(bb ~= 0)
    elseif op == "GETUPVAL" then
      r[aa] = V.expr("v2"..string.format("%02d", bb))
    elseif op == "SETUPVAL" then
      emit("v2"..string.format("%02d", bb).." = "..cv(r[aa]))
    elseif op == "CLOSURE" then
      local child = plist and plist[bb+1]
      if child then
        local sc, sk, sp, sm = decode(child, info, opmap, decoder)
        local body = dec(sc, sk, sp, sm, info, opmap, decoder, opn, indent.."  ", false, opts)
        local params = {}
        local np = sm.nparam
        for i = 1, np do params[i] = "v"..(i-1) end
        if sm.isvarag ~= 0 then table.insert(params, "...") end
        r[aa] = V.expr("function("..table.concat(params, ", ")..")\n"..body.."\n"..indent.."end")
      else
        r[aa] = V.expr("function() end")
      end
    elseif op == "ADD" or op == "SUB" or op == "MUL" or op == "DIV" or op == "MOD" or
      op == "POW" or op == "IDIV" or op == "CONCAT" then
      local sy = {ADD = "+", SUB = "-", MUL = "*", DIV = "/", MOD = "%",
                  POW = "^", IDIV = "//", CONCAT = ".."}
      r[aa] = V.expr("("..cv(r[bb]).." "..sy[op].." "..cv(r[cc])..")")
    elseif op == "EQ" or op == "NE" or op == "LT" or op == "GT" or op == "LE" or op == "GE" then
      local sy = {EQ = "==", NE = "~=", LT = "<", GT = ">", LE = "<=", GE = ">="}
      r[aa] = V.expr("("..cv(r[bb]).." "..sy[op].." "..cv(r[cc])..")")
    elseif op == "GETTABLE" then
      r[aa] = idxaccess(r[bb], r[cc])
    elseif op == "SETTABLE" then
      local t = cv(r[aa])
      local kr = rv(r[bb])
      local vc = cv(r[cc])
      local stmt
      if type(kr) == "string" and isident(kr) then
        stmt = t.."."..kr.." = "..vc
      elseif type(kr) == "string" then
        stmt = string.format("%s[%q] = %s", t, kr, vc)
      elseif type(kr) == "number" then
        stmt = t.."["..kr.."] = "..vc
      else
        stmt = t.."["..cv(r[bb]).."] = "..vc
      end
      if t:sub(1, 1) == "{" then
        if type(kr) == "string" and isident(kr) then
          stmt = ";("..t..")."..kr.." = "..vc
        elseif type(kr) == "string" then
          stmt = ";("..t..")["..string.format("%q", kr).."] = "..vc
        elseif type(kr) == "number" then
          stmt = ";("..t..")["..kr.."] = "..vc
        else
          stmt = ";("..t..")["..cv(r[bb]).."] = "..vc
        end
      end
      emit(stmt)
    elseif op == "SELF" then
      r[aa+1] = r[bb]
      r[aa] = idxaccess(r[bb], r[cc])
    elseif op == "CALL" then
      local nargs = bb == 0 and 0 or bb - 1
      local nret = cc == 0 and 0 or cc - 1
      local si = findselfbefore(ip, aa)
      local cs
      if nargs >= 1 and si then
        local oc = cv(r[aa+1])
        local fc = cv(r[aa])
        if fc:sub(1, #oc+1) == oc.."." then
          local m = fc:sub(#oc+2)
          if isident(m) then
            local ar = {}
            for i = 2, nargs do ar[i-1] = cv(r[aa+i]) end
            cs = oc..":"..m.."("..table.concat(ar, ", ")..")"
          end
        end
      end
      if not cs then
        local ar = {}
        for i = 1, nargs do ar[i] = cv(r[aa+i]) end
        cs = cv(r[aa]).."("..table.concat(ar, ", ")..")"
      end
      if nret == 0 then
        emit(cs)
        for i = 1, nargs do r[aa+i] = nil end
      else
        local lhs = {}
        for i = 0, nret - 1 do
          local nm = "v"..(aa+i)
          lhs[i+1] = nm
          r[aa+i] = V.lit(nm)
        end
        emit("local "..table.concat(lhs, ", ").." = "..cs)
        for i = 1, nargs do r[aa+i] = nil end
      end
    elseif op == "TAILCALL" then
      local nr = bb == 0 and 0 or bb - 1
      if nr > 0 then
        local vv = {}
        for i = 1, nr do vv[i] = cv(r[aa+i-1]) end
        emit("return "..table.concat(vv, ", "))
      end
    elseif op == "RETURN" then
      local nr = bb == 0 and 0 or bb - 1
      if nr == 0 then
        if not main or ip ~= n then emit("return") end
      elseif nr == 1 then
        local v = cv(r[aa])
        if v ~= "_" then emit("return "..v) end
      else
        local vv = {}
        for i = 1, nr do vv[i] = cv(r[aa+i-1]) end
        emit("return "..table.concat(vv, ", "))
      end
    elseif op == "VARARG" then
      local no = bb == 0 and 0 or bb - 1
      for i = 0, no - 1 do
        r[aa+i] = V.expr("(select("..(i+1)..",...))")
      end
    elseif op == "SETLIST" then
      local count = bb
      if count == 0 then
        if cf then emit("-- [control-flow: SETLIST]") end
      else
        local t = cv(r[aa])
        for i = 1, count do
          emit(t.."["..i.."] = "..cv(r[aa+i]))
          r[aa+i] = nil
        end
      end
    elseif op == "TEST" or op == "FORPREP" or op == "FORLOOP" or op == "TFORCALL" then
      if cf then emit("-- [control-flow: "..op.."]") end
    else
      if cf then emit("-- "..op.." A="..aa.." B="..bb.." C="..cc) end
    end
    ip = ip + 1
  end
  return table.concat(out, "\n")
end

return {decode = decode, dec = dec}
