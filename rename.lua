local function rename(text)
  local dir = (arg[0] or ""):match("^(.*[\\/])") or ""
  local rpath = dir.."renamer.py"
  local f = io.open(rpath, "r")
  if not f then return nil, "renamer.py not found at "..rpath end
  f:close()
  local tmp = os.tmpname()
  local fi = io.open(tmp, "w")
  fi:write(text)
  fi:close()
  local cmd = string.format("python3 %q %q 2>/dev/null", rpath, tmp)
  local p = io.popen(cmd, "r")
  if not p then
    os.remove(tmp)
    return nil, "failed to run python3"
  end
  local result = p:read("*a")
  p:close()
  os.remove(tmp)
  return result
end
return rename
