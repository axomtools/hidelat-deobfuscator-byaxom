This is a full deobfuscator for hide.lat lite preset 
made by axom. 

# USAGE 
`obfuscated.lua` → replace with your input file name
`output.lua` → replace with any file name you want as the output file
`-r/--rename` → renames variables to meaningful names
`--cfcomments` → adds control flow comments
alias :
`--cf`

```lua5.3 main.lua obfuscated.lua```
```lua5.3 main.lua obfuscated.lua output.lua```
```lua5.3 main.lua -r obfuscated.lua```
```lua5.3 main.lua --cfcomments obfuscated.lua```
```lua5.3 main.lua -r --cfcomments obfuscated.lua output.lua```

# INSTALLATION / REQUIREMENTS

YOU NEED :
- Lua5.3 and Python3

Install on Android :
```
pkg update
pkg install lua53 python```

Install on Debian,Ubuntu,Kali :
```
```
sudo apt update
sudo apt install lua5.3 python3```
```
Install on macOS :
brew install lua@5.3 python3
```
```
Install on Arch/Manjaro :
sudo pacman -S lua53 python
```
```
Install on Windows :
https://luabinaries.sourceforge.net/download.html
```
# ENJOY - BY AXOM
