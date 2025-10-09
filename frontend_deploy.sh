#!/bin/bash

# Tokyo Kafe - Frontend Deploy Script (Next.js)
# ==============================================

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tokyo Kafe - Frontend Deploy${NC}"
echo -e "${GREEN}========================================${NC}"

# Konfiguratsiya
BEGET_USER="u1234567"  # O'zingizning username
FRONTEND_DIR="/home/$BEGET_USER/public_html/frontend"
BACKEND_URL="https://tokyokafe.uz"  # Backend API URL
NODE_VERSION="18"  # Node.js versiyasi

# 1. Frontend papkasiga o'tish
echo -e "\n${YELLOW}[1/8]${NC} Frontend papkasiga o'tish..."
cd $FRONTEND_DIR || {
    echo -e "${RED}❌ Frontend papka topilmadi: $FRONTEND_DIR${NC}"
    exit 1
}
echo -e "${GREEN}✅ Hozirgi papka: $(pwd)${NC}"

# 2. Node.js versiyasini tekshirish
echo -e "\n${YELLOW}[2/8]${NC} Node.js versiyasini tekshirish..."
if command -v node &> /dev/null; then
    NODE_VER=$(node -v)
    echo -e "${GREEN}✅ Node.js versiyasi: $NODE_VER${NC}"
else
    echo -e "${RED}❌ Node.js o'rnatilmagan!${NC}"
    echo -e "${YELLOW}Node.js o'rnatish: nvm install $NODE_VERSION${NC}"
    exit 1
fi

# 3. .env.production faylini yaratish/tekshirish
echo -e "\n${YELLOW}[3/8]${NC} Environment o'zgaruvchilarni sozlash..."
if [ ! -f ".env.production" ]; then
    cat > .env.production << EOF
# Production Environment Variables
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_SITE_URL=https://tokyokafe.uz
NODE_ENV=production
EOF
    echo -e "${GREEN}✅ .env.production yaratildi${NC}"
else
    echo -e "${GREEN}✅ .env.production mavjud${NC}"
fi

# 4. Dependencies o'rnatish
echo -e "\n${YELLOW}[4/8]${NC} Dependencies o'rnatish..."
npm install --production=false
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies o'rnatildi${NC}"
else
    echo -e "${RED}❌ Dependencies o'rnatishda xatolik${NC}"
    exit 1
fi

# 5. Eski build ni o'chirish
echo -e "\n${YELLOW}[5/8]${NC} Eski build ni tozalash..."
rm -rf .next
echo -e "${GREEN}✅ Eski build o'chirildi${NC}"

# 6. Production build
echo -e "\n${YELLOW}[6/8]${NC} Production build qilish..."
echo -e "${BLUE}Bu jarayon bir necha daqiqa davom etishi mumkin...${NC}"
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build muvaffaqiyatli yakunlandi${NC}"
else
    echo -e "${RED}❌ Build xatosi! Loglarni tekshiring${NC}"
    exit 1
fi

# 7. PM2 orqali restart (agar PM2 mavjud bo'lsa)
echo -e "\n${YELLOW}[7/8]${NC} Next.js serverni qayta ishga tushirish..."
if command -v pm2 &> /dev/null; then
    pm2 stop tokyo-frontend 2>/dev/null
    pm2 delete tokyo-frontend 2>/dev/null
    pm2 start npm --name "tokyo-frontend" -- start -- -p 3000
    pm2 save
    echo -e "${GREEN}✅ PM2 orqali ishga tushirildi${NC}"
else
    echo -e "${YELLOW}⚠️  PM2 o'rnatilmagan. Manual start qiling: npm start${NC}"
fi

# 8. Build ma'lumotlari
echo -e "\n${YELLOW}[8/8]${NC} Build ma'lumotlari:"
if [ -d ".next" ]; then
    BUILD_SIZE=$(du -sh .next | cut -f1)
    echo -e "${GREEN}Build hajmi: $BUILD_SIZE${NC}"
    echo -e "${GREEN}Build papka: $FRONTEND_DIR/.next${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ FRONTEND DEPLOY MUVAFFAQIYATLI!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Frontend URL: https://tokyokafe.uz${NC}"
echo -e "${GREEN}Backend API: $BACKEND_URL${NC}"
echo -e "\n${YELLOW}Keyingi qadamlar:${NC}"
echo -e "${YELLOW}1. Nginx konfiguratsiyasini tekshiring${NC}"
echo -e "${YELLOW}2. Browser cache ni tozalang (Ctrl+Shift+R)${NC}"
echo -e "${YELLOW}3. Saytni tekshiring: https://tokyokafe.uz${NC}"

