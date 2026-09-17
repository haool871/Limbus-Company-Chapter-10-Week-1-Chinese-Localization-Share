#!/usr/bin/env bash
# 用法: bash tools/mk.sh <骨架名> <python片段文件>
# 片段里需定义 T=（必须）与 S=（可选）两个 dict；键为 "id|index"
set -euo pipefail
name="$1"; frag="$2"
cd "$(dirname "$0")/.."
tmp="$(mktemp /tmp/parts-XXXX.json)"
python3 -c '
import json,sys
ns={}
exec(open(sys.argv[1],encoding="utf-8").read(), ns)
json.dump({"T":ns.get("T",{}), "S":ns.get("S",{})}, open(sys.argv[2],"w",encoding="utf-8"), ensure_ascii=False)
' "$frag" "$tmp"
python3 tools/make_parts.py "$name" "$tmp"
rm -f "$tmp"
