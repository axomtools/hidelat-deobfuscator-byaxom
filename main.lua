local dir = (arg[0] or ""):match("^(.*[\\/])") or ""
package.path = dir.."?.lua;"..package.path

local analyze = require("analyze")
local capture = require("capture")
local findrt = require("findrt")
local classify = require("classify")
local decompile = require("decompile")
local rename = require("rename")

local inpath, outpath, dorename, docf
for i = 1, #arg do
  local a = arg[i]
  if a == "-r" or a == "--rename" then
    dorename = true
  elseif a == "--cfcomments" or a == "--cf" then
    docf = true
  elseif not inpath then
    inpath = a
  elseif not outpath then
    outpath = a
  end
end

if not inpath then
  error("usage: main.lua [-r|--rename] [--cfcomments] <input.lua> [output.lua]")
end

outpath = outpath or inpath:gsub("%.[^%.]+$", "")..".clean.lua"

local fh, ferr = io.open(inpath, "r")
if not fh then error("cannot open input: "..tostring(ferr)) end
local src = fh:read("*a")
fh:close()

local info = analyze(src)
local rt = capture(src)
local proto, opmap, decoder, dn, envn = findrt(rt)
local opn = classify(info, dn, envn)
local code, consts, plist, pmeta = decompile.decode(proto, info, opmap, decoder)
local text = decompile.dec(code, consts, plist, pmeta, info, opmap, decoder, opn, "", true, {cf = docf})

if dorename then
  local renamed, err = rename(text)
  if renamed then
    text = renamed
    print("Renamed.")
  else
    print("Rename skipped: "..tostring(err))
  end
end

local oh = io.open(outpath, "w")
oh:write(text.."\n")
oh:close()
print("Wrote: "..outpath)
