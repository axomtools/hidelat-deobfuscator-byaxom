import re
import sys
import argparse
import bisect

keywords = {"and","break","do","else","elseif","end","false","for","function","if","in","local","nil","not","or","repeat","return","then","true","until","while","continue","self"}

libmethods = {
    "math.random":"MathRandom","math.randomseed":"MathRandomSeed","math.floor":"MathFloor","math.ceil":"MathCeil","math.abs":"MathAbs","math.clamp":"MathClamp","math.min":"MathMin","math.max":"MathMax","math.rad":"MathRad","math.deg":"MathDeg","math.sqrt":"MathSqrt","math.sin":"MathSin","math.cos":"MathCos","math.tan":"MathTan","math.asin":"MathAsin","math.acos":"MathAcos","math.atan":"MathAtan","math.atan2":"MathAtan2","math.sinh":"MathSinh","math.cosh":"MathCosh","math.tanh":"MathTanh","math.log":"MathLog","math.log10":"MathLog10","math.exp":"MathExp","math.pow":"MathPow","math.frexp":"MathFrexp","math.ldexp":"MathLdexp","math.modf":"MathModf","math.fmod":"MathFmod","math.noise":"MathNoise","math.round":"MathRound","math.sign":"MathSign","math.lerp":"MathLerp","math.map":"MathMap","math.huge":"MathHuge","math.pi":"MathPi","math.nan":"MathNaN",
    "table.insert":"TableInsert","table.remove":"TableRemove","table.concat":"TableConcat","table.find":"TableFind","table.sort":"TableSort","table.unpack":"TableUnpack","table.pack":"TablePack","table.create":"TableCreate","table.clear":"TableClear","table.clone":"TableClone","table.freeze":"TableFreeze","table.isfrozen":"TableIsFrozen","table.maxn":"TableMaxN","table.move":"TableMove","table.foreach":"TableForeach","table.foreachi":"TableForeachi","table.getn":"TableGetN",
    "string.format":"StringFormat","string.sub":"StringSub","string.upper":"StringUpper","string.lower":"StringLower","string.rep":"StringRep","string.split":"StringSplit","string.gsub":"StringGsub","string.match":"StringMatch","string.find":"StringFind","string.gmatch":"StringGmatch","string.len":"StringLen","string.byte":"StringByte","string.char":"StringChar","string.reverse":"StringReverse","string.pack":"StringPack","string.unpack":"StringUnpack","string.packsize":"StringPackSize","string.dump":"StringDump",
    "task.wait":"TaskWait","task.spawn":"TaskSpawn","task.delay":"TaskDelay","task.defer":"TaskDefer","task.cancel":"TaskCancel","task.synchronize":"TaskSync","task.desynchronize":"TaskDesync",
    "coroutine.create":"CoroutineCreate","coroutine.resume":"CoroutineResume","coroutine.yield":"CoroutineYield","coroutine.status":"CoroutineStatus","coroutine.wrap":"CoroutineWrap","coroutine.running":"CoroutineRunning","coroutine.isyieldable":"CoroutineIsYieldable","coroutine.close":"CoroutineClose",
    "os.time":"OsTime","os.date":"OsDate","os.clock":"OsClock","os.difftime":"OsDiffTime","os.getenv":"OsGetEnv",
    "utf8.char":"Utf8Char","utf8.codepoint":"Utf8CodePoint","utf8.len":"Utf8Len","utf8.offset":"Utf8Offset","utf8.codes":"Utf8Codes","utf8.graphemes":"Utf8Graphemes",
    "bit32.band":"Bit32Band","bit32.bor":"Bit32Bor","bit32.bxor":"Bit32Bxor","bit32.bnot":"Bit32Bnot","bit32.lshift":"Bit32LShift","bit32.rshift":"Bit32RShift","bit32.arshift":"Bit32ArShift","bit32.lrotate":"Bit32LRotate","bit32.rrotate":"Bit32RRotate","bit32.btest":"Bit32BTest","bit32.extract":"Bit32Extract","bit32.replace":"Bit32Replace","bit32.countlz":"Bit32CountLZ","bit32.countrz":"Bit32CountRZ",
    "debug.traceback":"DebugTraceback","debug.info":"DebugInfo","debug.getinfo":"DebugGetInfo","debug.profilebegin":"DebugProfileBegin","debug.profileend":"DebugProfileEnd","debug.getmemorycategory":"DebugGetMemoryCategory","debug.setmemorycategory":"DebugSetMemoryCategory","debug.resetmemorycategory":"DebugResetMemoryCategory","debug.upvalues":"DebugUpvalues","debug.getupvalue":"DebugGetUpvalue","debug.setupvalue":"DebugSetUpvalue","debug.getlocal":"DebugGetLocal","debug.setlocal":"DebugSetLocal","debug.getregistry":"DebugGetRegistry","debug.getmetatable":"DebugGetMetatable","debug.setmetatable":"DebugSetMetatable","debug.getfenv":"DebugGetFenv","debug.setfenv":"DebugSetFenv","debug.sethook":"DebugSetHook","debug.gethook":"DebugGetHook","debug.debug":"DebugDebug","debug.getuservalue":"DebugGetUserValue","debug.setuservalue":"DebugSetUserValue",
    "buffer.create":"BufferCreate","buffer.fromstring":"BufferFromString","buffer.tostring":"BufferToString","buffer.len":"BufferLen","buffer.copy":"BufferCopy","buffer.fill":"BufferFill","buffer.readi8":"BufferReadI8","buffer.readu8":"BufferReadU8","buffer.readi16":"BufferReadI16","buffer.readu16":"BufferReadU16","buffer.readi32":"BufferReadI32","buffer.readu32":"BufferReadU32","buffer.readf32":"BufferReadF32","buffer.readf64":"BufferReadF64","buffer.writei8":"BufferWriteI8","buffer.writeu8":"BufferWriteU8","buffer.writei16":"BufferWriteI16","buffer.writeu16":"BufferWriteU16","buffer.writei32":"BufferWriteI32","buffer.writeu32":"BufferWriteU32","buffer.writef32":"BufferWriteF32","buffer.writef64":"BufferWriteF64",
    "vector.create":"VectorCreate","vector.magnitude":"VectorMagnitude","vector.normalize":"VectorNormalize","vector.cross":"VectorCross","vector.dot":"VectorDot","vector.angle":"VectorAngle","vector.floor":"VectorFloor","vector.ceil":"VectorCeil","vector.abs":"VectorAbs","vector.sign":"VectorSign","vector.clamp":"VectorClamp","vector.min":"VectorMin","vector.max":"VectorMax","vector.zero":"VectorZero","vector.one":"VectorOne","vector.xAxis":"VectorXAxis","vector.yAxis":"VectorYAxis","vector.zAxis":"VectorZAxis",
    "json.encode":"JsonEncode","json.decode":"JsonDecode",
    "bit.band":"BitBand","bit.bor":"BitBor","bit.bxor":"BitBxor","bit.bnot":"BitBnot","bit.lshift":"BitLShift","bit.rshift":"BitRShift","bit.arshift":"BitArShift","bit.rol":"BitRol","bit.ror":"BitRor","bit.bswap":"BitBswap","bit.tohex":"BitToHex",
}

globalfunctions = {
    "pcall":"PcallOk","xpcall":"XpcallOk","assert":"Asserted","type":"TypeName","typeof":"TypeName","tostring":"ToString","tonumber":"ToNumber","ipairs":"IPairsIterator","pairs":"PairsIterator","next":"NextItem","select":"Selected","unpack":"Unpacked","rawget":"RawValue","rawset":"RawTable","rawequal":"RawEqual","rawlen":"RawLength","getmetatable":"Metatable","setmetatable":"WithMetatable","newproxy":"NewProxy","require":"Module","collectgarbage":"Collected","loadstring":"LoadedFunction","load":"LoadedFunction","getfenv":"GetFenv","setfenv":"SetFenv","getgenv":"GetGenv","getsenv":"GetScriptEnv","getrenv":"GetRobloxEnv","getreg":"GetRegistry","getmenv":"GetModuleEnv","error":"ErrorMessage","tick":"Tick","time":"Time","elapsedTime":"ElapsedTime","wait":"Elapsed","spawn":"Thread","delay":"Thread","settings":"Settings","stats":"Stats","print":"Printed","warn":"Warned","IsA":"IsType","writefile":"WriteFile","readfile":"ReadFile","appendfile":"AppendFile","makefolder":"MakeFolder","delfile":"DeleteFile","delfolder":"DeleteFolder","listfiles":"ListFiles","isfile":"IsFile","isfolder":"IsFolder","loadfile":"LoadFile","dofile":"DoFile","getupvalue":"GetUpvalue","getupvalues":"GetUpvalues","setupvalue":"SetUpvalue","upvalues":"Upvalues","getrawmetatable":"GetRawMetatable","setrawmetatable":"SetRawMetatable","hookfunction":"HookFunction","hookmetamethod":"HookMetamethod","getnamecallmethod":"GetNamecallMethod","setnamecallmethod":"SetNamecallMethod","checkcaller":"CheckCaller","islclosure":"IsLClosure","iscclosure":"IsCClosure","newcclosure":"NewCClosure","clonefunction":"CloneFunction","restorefunction":"RestoreFunction","getfunctionhash":"GetFunctionHash","getconstant":"GetConstant","getconstants":"GetConstants","getgc":"GetGC","getinstances":"GetInstances","getnilinstances":"GetNilInstances","getscripts":"GetScripts","getloadedmodules":"GetLoadedModules","getrunningscripts":"GetRunningScripts","fireclickdetector":"FireClickDetector","firetouchinterest":"FireTouchInterest","fireproximityprompt":"FireProximityPrompt","firesignal":"FireSignal","getconnections":"GetConnections","getcustomasset":"GetCustomAsset","getcallbackvalue":"GetCallbackValue","getrenderstepped":"GetRenderStepped","getheartbeat":"GetHeartbeat","getstepped":"GetStepped","identifyexecutor":"IdentifyExecutor","getexecutorname":"GetExecutorName","getscriptbytecode":"GetScriptBytecode","getscripthash":"GetScriptHash","getscriptclosure":"GetScriptClosure","getscriptfromthread":"GetScriptFromThread","request":"Request","httprequest":"HttpRequest","synrequest":"SynRequest","setclipboard":"SetClipboard","toclipboard":"ToClipboard","mouse1click":"Mouse1Click","mouse1press":"Mouse1Press","mouse1release":"Mouse1Release","mouse2click":"Mouse2Click","mouse2press":"Mouse2Press","mouse2release":"Mouse2Release","mousemoveabs":"MouseMoveAbs","mousemoverel":"MouseMoveRel","mousescroll":"MouseScroll","keypress":"KeyPress","keyrelease":"KeyRelease","keytap":"KeyTap","iskeydown":"IsKeyDown","iskeypressed":"IsKeyPressed","getmouseposition":"GetMousePosition","getmousestate":"GetMouseState","setfflag":"SetFFlag","getfflag":"GetFFlag","getthreadidentity":"GetThreadIdentity","setthreadidentity":"SetThreadIdentity","getidentity":"GetIdentity","setidentity":"SetIdentity","getcallingscript":"GetCallingScript","decompile":"Decompile","setreadonly":"SetReadOnly","isreadonly":"IsReadOnly","isexecutorclosure":"IsExecutorClosure","isexecutor":"IsExecutor","getactors":"GetActors","gethui":"GetHui","getimmersivemode":"GetImmersiveMode","setimmersivemode":"SetImmersiveMode","isrenderobj":"IsRenderObj","getrenderproperty":"GetRenderProperty","setrenderproperty":"SetRenderProperty","cleardrawcache":"ClearDrawCache","drawingnew":"DrawingNew","getscriptsource":"GetScriptSource","getmenv2":"GetModuleEnv2","getscriptthread":"GetScriptThread","getthreads":"GetThreads","getproperties":"GetProperties","getattributes":"GetAttributes","getsignals":"GetSignals","getprotos":"GetProtos","getupvals":"GetUpvalues","getrawproperty":"GetRawProperty","setrawproperty":"SetRawProperty","gethiddenproperty":"GetHiddenProperty","sethiddenproperty":"SetHiddenProperty","setcallbackvalue":"SetCallbackValue","writecustomasset":"WriteCustomAsset",
}

methodnames = {
    "Wait":"Elapsed","Connect":"Connection","Once":"Connection","Clone":"Clone","Destroy":"Destroyed","ClearAllChildren":"Cleared","GetChildren":"Children","GetDescendants":"Descendants","GetPlayers":"PlayerList","GetTagged":"Tagged","GetInstanceAddedSignal":"Signal","GetInstanceRemovedSignal":"Signal","GetDataStore":"DataStore","GetOrderedDataStore":"OrderedDataStore","GetGlobalDataStore":"GlobalDataStore","GetCollisionGroupId":"GroupId","GetCollisionGroupName":"GroupName","CreatePath":"Path","Create":"Created","JSONEncode":"Json","JSONDecode":"Decoded","HttpGetAsync":"Response","HttpPostAsync":"Response","GetAsync":"Value","SetAsync":"Value","UpdateAsync":"Value","IncrementAsync":"Value","Kick":"Kicked","GetMouse":"Mouse","GetPropertyChangedSignal":"Signal","GetAttributeChangedSignal":"Signal","GetAttribute":"Value","SetAttribute":"Attribute","GetPivot":"Pivot","PivotTo":"Pivot","GetFullName":"FullName","GetDebugId":"DebugId","FindFirstAncestor":"Ancestor","FindFirstAncestorOfClass":"Ancestor","FindFirstAncestorWhichIsA":"Ancestor","IsA":"IsType","AddTag":"Tag","RemoveTag":"Tag","HasTag":"HasTag","GetTags":"Tags","WaitForChild":"Child","FindFirstChild":"Child","FindFirstChildOfClass":"Child","FindFirstChildWhichIsA":"Child","SetPrimaryPartCFrame":"Pivot","GetPrimaryPartCFrame":"Pivot","MoveTo":"Pivot","LoadCharacter":"Character","LoadCharacterWithHumanoidDescription":"Character","GetRankInGroup":"Rank","GetRoleInGroup":"Role","IsInGroup":"IsInGroup","IsFriendsWith":"IsFriend","GetFriendsAsync":"Friends","GetUserIdFromNameAsync":"UserId","GetNameFromUserIdAsync":"UserName","GetUserThumbnailAsync":"Thumbnail","GetProductInfo":"ProductInfo","UserOwnsGamePassAsync":"OwnsGamePass","PromptGamePassPurchase":"Prompt","PromptProductPurchase":"Prompt","PromptPurchase":"Prompt","GetDeveloperProductsAsync":"Products","GetStorePages":"Pages","GetService":"Service",
}


def normalizeclassname(name):
    parts = re.split(r"[\s_\-]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def isvalididentifier(s):
    return bool(re.fullmatch(r"[A-Za-z_]\w*", s))


def tocamel(name):
    if not name:
        return name
    return name[0].lower() + name[1:]


def joinsuffix(base, num):
    if base and base[-1].isdigit():
        return base + "_" + str(num)
    return base + str(num)


def striptrailingindex(e):
    m = re.match(r'^(.*?)\s*\[[^\]]*\]\s*$', e)
    if m:
        prefix = m.group(1)
        if '.' in prefix or ':' in prefix:
            return prefix
    return e


def startswithname(text, name):
    text = re.sub(r"--[^\n]*", "", text)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped)
    m = re.match(r'^\s*([A-Za-z_]\w*)', stripped)
    return bool(m and m.group(1) == name)


def readstmt(code, start):
    i = start
    n = len(code)
    depth = 0
    while i < n:
        c = code[i]
        if c == '"' or c == "'":
            q = c
            i += 1
            while i < n and code[i] != q:
                if code[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            continue
        if c == "-" and i + 1 < n and code[i + 1] == "-":
            j = code.find("\n", i)
            if j == -1:
                i = n
            else:
                i = j
            if depth == 0:
                return code[start:i], i
            continue
        if c == "[" and i + 1 < n and (code[i + 1] == "[" or code[i + 1] == "="):
            j = i + 1
            eq = 0
            while j < n and code[j] == "=":
                eq += 1
                j += 1
            if j < n and code[j] == "[":
                close = "]" + "=" * eq + "]"
                end = code.find(close, j + 1)
                i = n if end == -1 else end + len(close)
                continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth > 0:
                depth -= 1
        elif c == "\n" and depth == 0:
            return code[start:i], i
        i += 1
    return code[start:n], n


def splitcommas(text):
    parts = []
    depth = 0
    last = 0
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"' or c == "'":
            q = c
            i += 1
            while i < n and text[i] != q:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth > 0:
                depth -= 1
        elif c == "," and depth == 0:
            parts.append(text[last:i])
            last = i + 1
        i += 1
    parts.append(text[last:])
    return parts


def applymap(text, namemap):
    if not namemap:
        return text
    result = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"' or c == "'":
            start = i
            q = c
            i += 1
            while i < n and text[i] != q:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            result.append(text[start:i])
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            j = text.find("\n", i)
            if j == -1:
                j = n
            result.append(text[i:j])
            i = j
            continue
        if c.isalpha() or c == "_":
            m = re.match(r"[A-Za-z_]\w*", text[i:])
            word = m.group(0)
            k = i - 1
            while k >= 0 and text[k] in " \t\n\r":
                k -= 1
            isfield = k >= 0 and text[k] in ".:"
            if not isfield and word in namemap:
                result.append(namemap[word])
            else:
                result.append(word)
            i += len(word)
            continue
        result.append(c)
        i += 1
    return "".join(result)


def infername(expr):
    e = re.sub(r"--[^\n]*", "", expr).strip()
    if not e:
        return None

    m = re.match(r'^["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*$', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    e = striptrailingindex(e)

    m = re.match(r'^game\s*:\s*GetService\s*\(\s*["\']([^"\']+)["\']\s*\)\s*$', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'[.:]\s*GetService\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^Instance\s*\.\s*new\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^Enum\s*\.\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        t, v = m.group(1), m.group(2)
        n = (t + v) if len(v) <= 1 else v
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'[.:]\s*(?:WaitForChild|FindFirstChild|FindFirstChildOfClass|FindFirstChildWhichIsA)\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*\(', e)
    if m:
        dt, method = m.group(1), m.group(2)
        if method == "new" or method.startswith("from") or method.startswith("look") or method == "Angles" or method == "identity":
            n = dt
        else:
            n = normalizeclassname(method)
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        n = normalizeclassname(m.group(2))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-z_]\w*)\s*\.\s*([a-z_]\w*)\s*\(', e)
    if m:
        key = f"{m.group(1)}.{m.group(2)}"
        if key in libmethods:
            n = libmethods[key]
            return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-z_]\w*)\s*\.\s*([a-z_]\w*)\s*$', e)
    if m:
        key = f"{m.group(1)}.{m.group(2)}"
        if key in libmethods:
            n = libmethods[key]
            return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Za-z_]\w*)\s*\(', e)
    if m:
        fn = m.group(1)
        n = globalfunctions.get(fn, fn)
        return n if isvalididentifier(n) and n not in keywords else None

    methods = re.findall(r'[.:]\s*([A-Za-z_]\w*)\s*\(', e)
    if methods:
        method = methods[-1]
        n = methodnames.get(method, normalizeclassname(method))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", e)
    if m:
        field = m.group(1)
        if field[0].islower():
            n = field[0].upper() + field[1:]
        else:
            n = field
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]\s*$', e)
    if m:
        field = m.group(1)
        if field[0].islower():
            n = field[0].upper() + field[1:]
        else:
            n = field
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-zA-Z_]\w*)\s*$', e)
    if m:
        name = m.group(1)
        if name in keywords:
            return None
        n = name[0].upper() + name[1:] if name[0].islower() else name
        return n if isvalididentifier(n) and n not in keywords else None

    return None


def tokenize(code):
    tokens = []
    i = 0
    n = len(code)
    while i < n:
        c = code[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == "-" and i + 1 < n and code[i + 1] == "-":
            start = i
            if i + 3 < n and code[i + 2] == "[" and code[i + 3] == "[":
                end = code.find("]]", i + 4)
                i = n if end == -1 else end + 2
            else:
                end = code.find("\n", i)
                i = n if end == -1 else end
            tokens.append(("comment", code[start:i], start, i))
            continue
        if c == '"' or c == "'":
            start = i
            q = c
            i += 1
            while i < n and code[i] != q:
                if code[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            tokens.append(("string", code[start:i], start, i))
            continue
        if c == "[" and i + 1 < n and (code[i + 1] == "[" or code[i + 1] == "="):
            j = i + 1
            eq = 0
            while j < n and code[j] == "=":
                eq += 1
                j += 1
            if j < n and code[j] == "[":
                close = "]" + "=" * eq + "]"
                end = code.find(close, j + 1)
                stop = n if end == -1 else end + len(close)
                tokens.append(("string", code[i:stop], i, stop))
                i = stop
                continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (code[i].isalnum() or code[i] == "_"):
                i += 1
            word = code[start:i]
            tokens.append(("kw" if word in keywords else "ident", word, start, i))
            continue
        if c.isdigit() or (c == "." and i + 1 < n and code[i + 1].isdigit()):
            start = i
            while i < n and (code[i].isalnum() or code[i] in "._"):
                i += 1
            tokens.append(("num", code[start:i], start, i))
            continue
        tokens.append(("op", c, i, i + 1))
        i += 1
    return tokens


def findscopes(tokens):
    scopes = []
    stack = []
    awaitingdo = False
    for ti, tok in enumerate(tokens):
        if tok[0] != "kw":
            continue
        w = tok[1]
        if w in ("for", "while"):
            awaitingdo = True
            stack.append((ti, False, ti))
        elif w == "do":
            if awaitingdo:
                awaitingdo = False
            else:
                stack.append((ti, False, ti))
        elif w in ("function", "repeat"):
            stack.append((ti, False, ti))
        elif w == "if":
            stack.append((ti, True, ti))
        elif w in ("elseif", "else"):
            if stack and stack[-1][1]:
                openti, _, branchstart = stack.pop()
                scopes.append((branchstart, ti))
                stack.append((openti, True, ti))
        elif w in ("end", "until"):
            if stack:
                openti, isif, branchstart = stack.pop()
                scopes.append((branchstart, ti))
    return scopes


def collectassigns(tokens, code, n):
    assigns = {}
    ti = 0
    while ti < n - 1:
        tok = tokens[ti]
        if tok[0] != "ident":
            ti += 1
            continue
        op1 = tokens[ti + 1]
        if op1[0] != "op" or op1[1] != "=":
            ti += 1
            continue
        if ti + 2 < n and tokens[ti + 2][0] == "op" and tokens[ti + 2][1] == "=":
            ti += 2
            continue
        if ti > 0:
            prev = tokens[ti - 1]
            if prev[0] == "kw" and prev[1] == "for":
                ti += 1
                continue
            if prev[0] == "op" and prev[1] in ".:":
                ti += 1
                continue
        rhsstart = op1[3]
        rhstext, _ = readstmt(code, rhsstart)
        assigns.setdefault(tok[1], []).append((ti, rhstext))
        ti += 1
    return assigns


def renamecode(code):
    tokens = tokenize(code)
    n = len(tokens)
    if n == 0:
        return code

    scopes = findscopes(tokens)
    scopes.sort()
    scopestarts = [s[0] for s in scopes]

    def scopeendfor(ti):
        pos = bisect.bisect_right(scopestarts, ti) - 1
        while pos >= 0:
            s, e = scopes[pos]
            if e > ti:
                return e
            pos -= 1
        return n

    def scopechainof(ti):
        chain = [sid for sid, (s, e) in enumerate(scopes) if s <= ti < e]
        chain.sort(key=lambda sid: scopes[sid][0])
        return chain

    assigns = collectassigns(tokens, code, n)
    scopeused = {}

    renames = []
    ti = 0
    while ti < n:
        tok = tokens[ti]
        if tok[0] == "kw" and tok[1] == "local":
            names = []
            j = ti + 1
            while j < n:
                t = tokens[j]
                if t[0] == "ident":
                    names.append((j, t[1]))
                    j += 1
                    if j < n and tokens[j][0] == "op" and tokens[j][1] == ",":
                        j += 1
                        continue
                    else:
                        break
                else:
                    break

            if not names:
                ti += 1
                continue

            haseq = j < n and tokens[j][0] == "op" and tokens[j][1] == "="

            if haseq:
                rhsstart = tokens[j][3]
                rhstext, _ = readstmt(code, rhsstart)
                rhsparts = splitcommas(rhstext)
            else:
                rhsparts = []

            for idx, (nameti, oldname) in enumerate(names):
                if oldname.startswith("_"):
                    continue

                rawname = None
                swappedrhs = None

                if haseq and idx < len(rhsparts):
                    visible = {}
                    for (on, nn, dt, et) in renames:
                        if dt <= nameti < et:
                            visible[on] = nn
                    swappedrhs = applymap(rhsparts[idx], visible)
                    rawname = infername(swappedrhs)

                if not rawname:
                    scopeendti = scopeendfor(nameti)
                    for (ati, atext) in assigns.get(oldname, []):
                        if ati > nameti and ati < scopeendti:
                            visible = {}
                            for (on, nn, dt, et) in renames:
                                if dt <= ati < et:
                                    visible[on] = nn
                            swapped = applymap(atext, visible)
                            cand = infername(swapped)
                            if cand:
                                rawname = cand
                                swappedrhs = swapped
                                break

                if not rawname:
                    continue

                newname = tocamel(rawname)
                shadow = startswithname(swappedrhs, rawname)

                if newname == oldname and not shadow:
                    continue

                chain = scopechainof(nameti)
                seenchain = set(scopeused.get(-1, set()))
                for sid in chain:
                    seenchain |= scopeused.get(sid, set())

                if shadow:
                    candidate = joinsuffix(newname, 2)
                    suffix = 3
                else:
                    candidate = newname
                    suffix = 2
                while candidate in seenchain or candidate == oldname:
                    candidate = joinsuffix(newname, suffix)
                    suffix += 1
                if candidate == oldname:
                    continue

                if chain:
                    innermost = chain[-1]
                else:
                    innermost = -1
                scopeused.setdefault(innermost, set()).add(candidate)

                scopeendti = scopeendfor(nameti)
                renames.append((oldname, candidate, nameti, scopeendti))

        ti += 1

    if not renames:
        return code

    byname = {}
    for oldname, newname, declti, scopeendti in renames:
        byname.setdefault(oldname, []).append((newname, declti, scopeendti))

    ops = []
    for ti, tok in enumerate(tokens):
        if tok[0] != "ident":
            continue
        rules = byname.get(tok[1])
        if not rules:
            continue
        bestname = None
        bestdecl = -1
        for newname, declti, scopeendti in rules:
            if declti <= ti < scopeendti and declti > bestdecl:
                bestname = newname
                bestdecl = declti
        if bestname is not None:
            ops.append((tok[2], tok[3], bestname))

    if not ops:
        return code

    ops.sort()
    out = []
    last = 0
    for start, end, newtext in ops:
        if start < last:
            continue
        out.append(code[last:start])
        out.append(newtext)
        last = end
    out.append(code[last:])
    return "".join(out)


def main():
    p = argparse.ArgumentParser(
        prog="renamer",
        description="Renames Luau variables to inferred camelCase names.",
    )
    p.add_argument("input", nargs="?", default=None,
                   help="Input file (omit to read from stdin)")
    p.add_argument("output", nargs="?", default=None,
                   help="Output file (omit to write to stdout)")
    args = p.parse_args()

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except OSError as e:
            print(f"Error reading {args.input}: {e}", file=sys.stderr)
            return 1
    else:
        if sys.stdin.isatty():
            print("Renamer - paste code, then Ctrl+D to finish (Ctrl+C to cancel):", file=sys.stderr)
        code = sys.stdin.read()

    if not code:
        print("No input provided.", file=sys.stderr)
        return 1

    result = renamecode(code)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
        except OSError as e:
            print(f"Error writing {args.output}: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
