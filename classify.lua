local function classify(info, dn, envn)
  local r, a, bn, c = info.regs, info.an, info.bn, info.cn
  local hs = info.handlers
  local function esc(s) return (s:gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])", "%%%1")) end
  local rany = esc(r).."%[[%w_][%w_%+]*%]"
  local function rp(name) return esc(r).."%["..esc(name).."%]" end
  local function rpn(name, n) return esc(r).."%["..esc(name).."%+"..n.."%]" end
  local ra = rp(a)
  local raa1 = rpn(a, 1)
  local raa2 = rpn(a, 2)
  local rb = rp(bn)
  local function fl(n)
    for l in (hs[n] or ""):gmatch("[^\r\n]+") do
      local x = l:match("^%s*(.-)%s*;?%s*$")
      if x and #x > 0 and x:sub(1, 2) ~= "--" then return x end
    end
    return ""
  end
  local function fra(n)
    for l in (hs[n] or ""):gmatch("[^\r\n]+") do
      local x = l:match("^%s*(.-)%s*;?%s*$")
      local rr = x and x:match("^"..ra.."%s*=%s*(.-)%s*$")
      if rr then return rr end
    end
  end
  local function startsra(n)
    return fl(n):match("^local%s+[%w_]+%s*=%s*"..ra)
  end
  local opn = {}
  local function mf(b, pat) return b:find(pat) ~= nil end
  for n, b in pairs(hs) do
    if not mf(b, rany) then
      if b:match("^%s*[%w_]+%s*=%s*"..esc(bn).."%+1%s*;?%s*$") then
        opn[n] = "JMP"
      else
        opn[n] = "JUNK"
      end
    end
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t2 end
    if mf(b, "%(not not ") and mf(b, "~=0") and mf(b, "%+1") then opn[n] = "TEST" end
    ::t2::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t3 end
    if mf(b, "tonumber") or b:find("Numeric for bounds", 1, true) then opn[n] = "FORPREP" end
    ::t3::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t4 end
    local t = fl(n)
    if t:match("^local%s+[%w_]+%s*=%s*[%w_]+%["..esc(bn.."+1").."%]") and b:find("for ", 1, true) then
      opn[n] = "CLOSURE"
    end
    ::t4::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t5 end
    if startsra(n) and mf(b, raa1) and mf(b, raa2) and mf(b, "[%w_]+%(") and not mf(b, esc(bn).."==0") then
      opn[n] = "TFORCALL"
    end
    ::t5::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t6 end
    if startsra(n) and mf(b, ra.."%s*=%s*"..ra.."%s*%+%s*"..raa2)
      and mf(b, "%+1") and not mf(b, esc(bn).."==0") and not mf(b, "%.n") then
      opn[n] = "FORLOOP"
    end
    ::t6::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t7 end
    if startsra(n) and mf(b, esc(bn).."==0") and mf(b, "%.n") then opn[n] = "CALL" end
    ::t7::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t8 end
    if mf(b, esc(bn).."==0") and b:find("for ", 1, true) and not mf(b, ra.."%[") then
      opn[n] = "VARARG"
    end
    ::t8::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t9 end
    if mf(b, esc(bn).."==0") and b:find("for ", 1, true) and mf(b, ra.."%[") then
      opn[n] = "SETLIST"
    end
    ::t9::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t10 end
    if b:find("=nil", 1, true) and fl(n):match("^for%s+") and not mf(b, "[%w_]+%(") then
      opn[n] = "LOADNIL"
    end
    ::t10::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t11 end
    if mf(b, raa1.."%s*=%s*"..rb) and mf(b, esc(r).."%["..esc(bn).."%]%[") then
      opn[n] = "SELF"
    end
    ::t11::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t12 end
    local t = fl(n)
    local uvpat = "[%w_]+%["..esc(bn).."%+?%d*%]%[1%]"
    if t:match("^"..ra.."%s*=%s*"..uvpat.."%s*$") then
      opn[n] = "GETUPVAL"
    elseif b:find(uvpat.."%s*=%s*"..ra) then
      opn[n] = "SETUPVAL"
    end
    ::t12::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t13 end
    local t = fl(n)
    local dncall = esc(dn).."%("
    local envdn = esc(envn).."%["..dncall
    local raeq = ra.."%s*=%s*"
    if t:match("^"..raeq..dncall) and not t:match("^"..raeq..envdn) then
      opn[n] = "LOADK"
    elseif t:match("^"..raeq..envdn) then
      opn[n] = "GETGLOBAL"
    elseif mf(b, envdn) and mf(b, "="..rany) then
      opn[n] = "SETGLOBAL"
    end
    ::t13::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t14 end
    if b:find("return%s+[%w_]+%(", 1) and mf(b, esc(bn).."==0") and not mf(b, "%.n") then
      opn[n] = "TAILCALL"
    end
    ::t14::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t15 end
    local t = fl(n)
    local raeq = ra.."%s*=%s*"
    if t:match("^"..raeq.."%{%s*%}%s*$") then
      opn[n] = "NEWTABLE"
    elseif t:match("^"..raeq.."%{[ %s]*"..rb.."[ %s]*%}%s*$") then
      opn[n] = "NEWTABLE1"
    elseif t:match("^"..raeq.."not%s+"..rany.."%s*$") then
      opn[n] = "NOT"
    elseif t:match("^"..raeq.."%-"..rany.."%s*$") and not b:find("+", 1, true) then
      opn[n] = "UNM"
    elseif t:match("^"..raeq.."#"..rany.."%s*$") then
      opn[n] = "LEN"
    elseif t:match("^"..raeq..rany.."%s*$") then
      opn[n] = "MOVE"
    elseif t:match("^"..raeq.."%(%s*"..esc(bn).."~=0%s*%)%s*$") then
      opn[n] = "LOADBOOL"
    end
    ::t15::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t16 end
    local rhs = fra(n)
    if rhs then
      rhs = rhs:match("^%((.+)%)$") or rhs
      rhs = rhs:match("^%((.+)%)$") or rhs
      local ops = {
        {"<=", "LE"}, {">=", "GE"}, {"~=", "NE"}, {"==", "EQ"},
        {"<", "LT"}, {">", "GT"},
        {"%+", "ADD"}, {"%-", "SUB"}, {"%*", "MUL"}, {"/", "DIV"},
        {"%%", "MOD"}, {"%^", "POW"},
        {"%.%.", "CONCAT"}, {"//", "IDIV"}
      }
      for _, o in ipairs(ops) do
        if rhs:match("^"..rany.."%s*"..o[1].."%s*"..rany.."%s*$") then
          opn[n] = o[2]
          goto t16
        end
      end
    end
    ::t16::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t17 end
    local t = fl(n)
    if t:match("^"..ra.."%s*=%s*"..rany.."%["..rany.."%]") then
      opn[n] = "GETTABLE"
    elseif t:match("^"..ra.."%["..rany.."%]%s*=%s*"..rany) then
      opn[n] = "SETTABLE"
    end
    ::t17::
  end
  for n, b in pairs(hs) do
    if opn[n] then goto t18 end
    if mf(b, "^%s*return") and mf(b, esc(bn).."==0") and not mf(b, "[%w_]+%(") then
      opn[n] = "RETURN"
    end
    ::t18::
  end
  for n in pairs(hs) do
    if not opn[n] then opn[n] = "UNK_"..n end
  end
  return opn
end
return classify
