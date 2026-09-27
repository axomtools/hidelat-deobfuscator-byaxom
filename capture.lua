local function capture(src)
  local lr, p = nil, 1
  while true do
    local s, e = src:find("\nreturn ", p, true)
    if not s then break end
    lr = s
    p = e + 1
  end
  local inj = "\ndo local a1={};local i=1 while true do local n,v=debug.getlocal(1,i) if not n then break end a1[n]=v;i=i+1 end zzqx=a1;error('__HALT__') end\n"
  local fn = assert(load(src:sub(1, lr)..inj..src:sub(lr+1), "@obf", "t"))
  local ok, err = pcall(fn)
  assert(type(err) == "string" and err:find("__HALT__"), tostring(err))
  return zzqx
end
return capture
