#!/bin/bash
#
# convert-to-webp.sh — 把資料夾裡的 JPG/PNG 轉成 WebP
#
# 用法：
#   bash convert-to-webp.sh <資料夾> [品質] [-r]
#
# 範例：
#   bash convert-to-webp.sh ~/Desktop/images            # 品質預設 80
#   bash convert-to-webp.sh ~/Desktop/images 90         # 指定品質 90
#   bash convert-to-webp.sh ~/Desktop/images 80 -r      # 連子資料夾一起轉
#

# 第一個參數 = 資料夾（沒帶就用目前所在資料夾）
SRC_DIR="${1:-.}"

# 第二個參數 = 品質（沒帶就 80）
QUALITY="${2:-80}"

# 有帶 -r 就遞迴子資料夾
RECURSIVE=false
if [ "$3" = "-r" ]; then
  RECURSIVE=true
fi

# ---- 檢查 ----
if ! command -v cwebp >/dev/null 2>&1; then
  echo "❌ 找不到 cwebp，請先安裝： brew install webp"
  exit 1
fi
if [ ! -d "$SRC_DIR" ]; then
  echo "❌ 找不到資料夾：$SRC_DIR"
  echo "   用法： bash convert-to-webp.sh <資料夾> [品質] [-r]"
  exit 1
fi

echo "來源：$SRC_DIR"
echo "品質：$QUALITY 遞迴：$RECURSIVE"
echo ""

count=0
skipped=0
find_depth=""
[ "$RECURSIVE" = false ] && find_depth="-maxdepth 1"

while IFS= read -r -d '' f; do
  out="${f%.*}.webp"
  if [ -f "$out" ]; then
    echo "⏭  跳過：$(basename "$out")"
    skipped=$((skipped + 1))
    continue
  fi
  if cwebp -q "$QUALITY" "$f" -o "$out" >/dev/null 2>&1; then
    echo "✅ $(basename "$f") → $(basename "$out")"
    count=$((count + 1))
  else
    echo "⚠️  失敗：$(basename "$f")"
  fi
done < <(find "$SRC_DIR" $find_depth -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0)

echo ""
echo "🎉 完成！成功 $count 張，跳過 $skipped 張（原圖保留）。"
