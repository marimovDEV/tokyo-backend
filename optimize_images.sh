#!/bin/bash

# Tokyo Kafe - Image Optimization Script
# =======================================
# Media rasmlarni optimize qilish

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tokyo Kafe - Rasmlarni Optimize Qilish${NC}"
echo -e "${GREEN}========================================${NC}"

BEGET_USER="u1234567"
MEDIA_DIR="/home/$BEGET_USER/public_html/backend/media"
BACKUP_DIR="/home/$BEGET_USER/media_backup_$(date +%Y%m%d)"

# 1. Backup yaratish
echo -e "\n${YELLOW}[1/5]${NC} Backup yaratish..."
if [ -d "$MEDIA_DIR" ]; then
    cp -r $MEDIA_DIR $BACKUP_DIR
    echo -e "${GREEN}✅ Backup: $BACKUP_DIR${NC}"
else
    echo -e "${RED}❌ Media papka topilmadi${NC}"
    exit 1
fi

# 2. ImageMagick o'rnatilganini tekshirish
echo -e "\n${YELLOW}[2/5]${NC} ImageMagick ni tekshirish..."
if ! command -v convert &> /dev/null; then
    echo -e "${RED}❌ ImageMagick o'rnatilmagan${NC}"
    echo -e "${YELLOW}O'rnatish: yum install ImageMagick (yoki apt install imagemagick)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ImageMagick mavjud${NC}"

# 3. Rasmlarni optimize qilish
echo -e "\n${YELLOW}[3/5]${NC} Rasmlarni optimize qilish..."

# JPG/JPEG rasmlar
echo -e "${BLUE}JPG rasmlar optimize qilinmoqda...${NC}"
find $MEDIA_DIR -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) -print0 | while IFS= read -r -d '' file; do
    echo "Optimize: $file"
    convert "$file" -strip -quality 85 -resize '2000x2000>' "$file"
done

# PNG rasmlar
echo -e "${BLUE}PNG rasmlar optimize qilinmoqda...${NC}"
find $MEDIA_DIR -type f -iname "*.png" -print0 | while IFS= read -r -d '' file; do
    echo "Optimize: $file"
    convert "$file" -strip -resize '2000x2000>' "$file"
done

# 4. WebP formatga konvertatsiya qilish (opsional)
echo -e "\n${YELLOW}[4/5]${NC} WebP formatga konvertatsiya..."
if command -v cwebp &> /dev/null; then
    find $MEDIA_DIR -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -print0 | while IFS= read -r -d '' file; do
        webp_file="${file%.*}.webp"
        if [ ! -f "$webp_file" ]; then
            echo "WebP: $webp_file"
            cwebp -q 85 "$file" -o "$webp_file"
        fi
    done
    echo -e "${GREEN}✅ WebP konvertatsiya tugadi${NC}"
else
    echo -e "${YELLOW}⚠️  cwebp o'rnatilmagan, WebP skip${NC}"
fi

# 5. Statistika
echo -e "\n${YELLOW}[5/5]${NC} Statistika:"
ORIGINAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
NEW_SIZE=$(du -sh $MEDIA_DIR | cut -f1)

echo -e "${BLUE}Eski hajm: $ORIGINAL_SIZE${NC}"
echo -e "${BLUE}Yangi hajm: $NEW_SIZE${NC}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ OPTIMIZE TUGADI!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Backup: $BACKUP_DIR${NC}"
echo -e "${YELLOW}Agar muammo bo'lsa: cp -r $BACKUP_DIR/* $MEDIA_DIR/${NC}"

