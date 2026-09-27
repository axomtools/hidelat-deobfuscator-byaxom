local function analyze(src)
  local opmap = src:match("local%s+([%w_]+)%s*=%s*{}[\r\n]+%s*local%s+[%w_]+%s*=[%w_]+%(%)[\r\n]+%s*for")
  assert(opmap, "opmap not found")
  local opvar = src:match("local%s+([%w_]+)%s*=%s*"..opmap.."%[[%w_]+%]")
  local seedpat = "%([^%(%)]+%s*%+%s*([%w_]+)%s*%*65599%s*%)%s*%%%s*4294967296"
  local seed = src:match("local%s+([%w_]+)%s*="..seedpat)
  assert(seed, "seed not found")
  local ds, disp, p = nil, nil, 1
  while true do
    local s = src:find("while%s+true%s+do", p)
    if not s then break end
    local c = src:sub(s, s+30000)
    if c:find(opvar, 1, true) then ds = s; disp = c; break end
    p = s + 10
  end
  assert(disp, "dispatcher not found")
  local inst = disp:match("local%s+([%w_]+)%s*=%s*([%w_]+)%[[%w_]+%]")
  local fds = {}
  p = 1
  while true do
    local s, e, n, i, m = disp:find(
      "local%s+([%w_]+)%s*=%s*%("..inst.."%[(%d)%]%s*%-%s*"..seed.."%s*%)%s*%%%s*(%d+)", p)
    if not s then break end
    table.insert(fds, {name = n, idx = tonumber(i), mod = tonumber(m)})
    p = e + 1
  end
  assert(#fds == 4, "expected 4 fields, got "..#fds)
  local an, bn, cn = fds[2].name, fds[3].name, fds[4].name
  local res = {}
  for pos, n in (disp.."\n"):gmatch("()if%s+"..opvar.."%s*==%s*(%d+)%s+then") do
    table.insert(res, {pos = pos, n = tonumber(n)})
  end
  for pos, n in (disp.."\n"):gmatch("()elseif%s+"..opvar.."%s*==%s*(%d+)%s+then") do
    table.insert(res, {pos = pos, n = tonumber(n)})
  end
  table.sort(res, function(a, b) return a.pos < b.pos end)
  local ep = nil
  for i = #res, 1, -1 do
    local candidate = disp:find("\nelse[%s%w]", res[i].pos)
    if candidate then ep = candidate; break end
  end
  ep = ep or #disp
  local hs = {}
  for i = 1, #res do
    local r = res[i]
    local _, te = disp:sub(r.pos):find("then")
    local be = i < #res and res[i+1].pos or ep
    hs[r.n] = disp:sub(r.pos + te, be - 1):match("^%s*(.-)%s*$")
  end
  local rv
  for _, body in pairs(hs) do
    local rn = body:match("([%w_]+)%["..an.."%]%s*=")
    if rn then rv = rn; break end
  end
  assert(rv, "register name not found")
  return {
    opmap = opmap,
    opvar = opvar,
    seed = seed,
    inst = inst,
    regs = rv,
    fields = fds,
    an = an,
    bn = bn,
    cn = cn,
    handlers = hs
  }
end
return analyze
