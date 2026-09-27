local function findrt(rt)
  local proto
  for _, v in pairs(rt) do
    if type(v) == "table" and type(v[3]) == "table" and type(v[4]) == "table" and #v >= 8 then
      proto = v
    end
  end
  local opmap
  for _, v in pairs(rt) do
    if type(v) == "table" then
      local ok, c, mx = true, 0, -1/0
      for kk, vv in pairs(v) do
        if type(kk) ~= "number" or type(vv) ~= "number" then ok = false; break end
        c = c + 1
        mx = math.max(mx, vv)
      end
      if ok and c >= 30 and mx <= 50 then opmap = v end
    end
  end
  local kp = proto[4]
  local dec, dn, envn
  for k, v in pairs(rt) do
    if type(v) == "function" then
      local i2 = debug.getinfo(v, "uS")
      if i2.nparams == 3 and i2.what == "Lua" then
        local a, r1 = pcall(v, kp, {}, 1)
        local b = pcall(v, kp, {}, 2)
        if a and b and (type(r1) == "string" or type(r1) == "number" or type(r1) == "boolean") then
          if select(2, pcall(v, kp, {}, 1)) == r1 then dec = v; dn = k end
        end
      end
    end
    if type(v) == "table" and v.print == print then envn = k end
  end
  return proto, opmap, dec, dn, envn
end
return findrt
