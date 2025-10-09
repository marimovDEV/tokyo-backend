#!/bin/bash

# Tokyo Kafe - Complete Server Restart Script
# ============================================
# Serverda ishlab turgan loyihani to'xtatib, qayta ishga tushirish

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Tokyo Kafe - Server Restart Script           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

# Konfiguratsiya
PROJECT_DIR="$HOME/tokyo"  # O'zingizning papka yo'lingiz
SERVICE_NAME="gunicorn"    # Service nomi (agar bo'lsa)

# ==========================================
# 1. Git Yangilash
# ==========================================

echo -e "\n${YELLOW}[1/6]${NC} Git yangilash va reset..."

if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR || exit 1
    
    echo -e "${BLUE}Git fetch...${NC}"
    git fetch origin
    
    echo -e "${BLUE}Git reset --hard origin/main...${NC}"
    git reset --hard origin/main
    
    echo -e "${GREEN}✅ Git yangilandi${NC}"
    git log --oneline -3
else
    echo -e "${RED}❌ Git repository topilmadi: $PROJECT_DIR${NC}"
fi

# ==========================================
# 2. Service Nomini Topish
# ==========================================

echo -e "\n${YELLOW}[2/6]${NC} Gunicorn service ni tekshirish..."

# Service mavjudligini tekshirish
if systemctl list-units --type=service | grep -q "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Service topildi: $SERVICE_NAME${NC}"
    USE_SERVICE=true
else
    echo -e "${YELLOW}⚠️  Systemd service topilmadi${NC}"
    USE_SERVICE=false
fi

# ==========================================
# 3. Eski Processlarni To'xtatish
# ==========================================

echo -e "\n${YELLOW}[3/6]${NC} Eski Gunicorn processlarni to'xtatish..."

if [ "$USE_SERVICE" = true ]; then
    # Service bilan to'xtatish
    echo -e "${BLUE}Systemd service to'xtatilmoqda...${NC}"
    sudo systemctl stop $SERVICE_NAME
    sleep 2
    echo -e "${GREEN}✅ Service to'xtatildi${NC}"
else
    # Manual to'xtatish
    GUNICORN_PIDS=$(ps aux | grep '[g]unicorn' | awk '{print $2}')
    
    if [ ! -z "$GUNICORN_PIDS" ]; then
        echo -e "${YELLOW}Gunicorn processlar topildi:${NC}"
        echo "$GUNICORN_PIDS"
        
        echo -e "${BLUE}To'xtatilmoqda...${NC}"
        echo "$GUNICORN_PIDS" | xargs kill -TERM 2>/dev/null
        sleep 3
        
        # Agar hali ham ishlayotgan bo'lsa
        REMAINING=$(ps aux | grep '[g]unicorn' | awk '{print $2}')
        if [ ! -z "$REMAINING" ]; then
            echo -e "${YELLOW}Majburan to'xtatilmoqda...${NC}"
            echo "$REMAINING" | xargs kill -9 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ Gunicorn to'xtatildi${NC}"
    else
        echo -e "${GREEN}✅ Gunicorn processlar topilmadi${NC}"
    fi
fi

# ==========================================
# 4. Dependencies Tekshirish
# ==========================================

echo -e "\n${YELLOW}[4/6]${NC} Dependencies tekshirish..."

if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source $PROJECT_DIR/venv/bin/activate
    
    # Requirements yangilash (agar kerak bo'lsa)
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        echo -e "${BLUE}Requirements tekshirilmoqda...${NC}"
        pip install -q -r $PROJECT_DIR/requirements.txt
        echo -e "${GREEN}✅ Dependencies tayyor${NC}"
    fi
else
    echo -e "${RED}❌ Virtual environment topilmadi${NC}"
    exit 1
fi

# ==========================================
# 5. Migratsiyalar
# ==========================================

echo -e "\n${YELLOW}[5/6]${NC} Database migratsiyalari..."

cd $PROJECT_DIR
python manage.py migrate --noinput > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migratsiyalar bajarildi${NC}"
else
    echo -e "${YELLOW}⚠️  Migratsiya xatosi (davom ettirilmoqda)${NC}"
fi

# ==========================================
# 6. Gunicorn Qayta Ishga Tushirish
# ==========================================

echo -e "\n${YELLOW}[6/6]${NC} Gunicorn qayta ishga tushirish..."

if [ "$USE_SERVICE" = true ]; then
    # Service bilan ishga tushirish
    echo -e "${BLUE}Systemd service ishga tushirilmoqda...${NC}"
    sudo systemctl start $SERVICE_NAME
    sleep 3
    
    # Status tekshirish
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✅ Service muvaffaqiyatli ishga tushdi${NC}"
        sudo systemctl status $SERVICE_NAME --no-pager -l
    else
        echo -e "${RED}❌ Service ishga tushmadi!${NC}"
        sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
        exit 1
    fi
else
    # Manual ishga tushirish
    echo -e "${BLUE}Gunicorn manual ishga tushirilmoqda...${NC}"
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    if [ -f "gunicorn.conf.py" ]; then
        # Config file bilan
        gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application --daemon
    else
        # Default settings bilan
        gunicorn restaurant_api.wsgi:application \
            --bind 127.0.0.1:8000 \
            --workers 2 \
            --daemon \
            --access-logfile logs/gunicorn_access.log \
            --error-logfile logs/gunicorn_error.log
    fi
    
    sleep 2
    
    # Process tekshirish
    if ps aux | grep -q '[g]unicorn'; then
        echo -e "${GREEN}✅ Gunicorn muvaffaqiyatli ishga tushdi${NC}"
        ps aux | grep '[g]unicorn'
    else
        echo -e "${RED}❌ Gunicorn ishga tushmadi!${NC}"
        tail -20 logs/gunicorn_error.log
        exit 1
    fi
fi

# ==========================================
# 7. Tekshirish
# ==========================================

echo -e "\n${YELLOW}[TEST]${NC} Server ishlashini tekshirish..."

# Port 8000 tekshirish
if netstat -tuln 2>/dev/null | grep -q ':8000' || ss -tuln 2>/dev/null | grep -q ':8000'; then
    echo -e "${GREEN}✅ Port 8000 band (ishlayapti)${NC}"
else
    echo -e "${RED}❌ Port 8000 ochiq (ishlamayapti)${NC}"
fi

# API test
echo -e "${BLUE}API test qilinmoqda...${NC}"
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/menu/ 2>/dev/null)

if [ "$API_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ API ishlayapti (HTTP $API_RESPONSE)${NC}"
else
    echo -e "${YELLOW}⚠️  API javob bermadi (HTTP $API_RESPONSE)${NC}"
fi

# ==========================================
# Yakuniy Natija
# ==========================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ SERVER RESTART TUGADI!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}📊 Server Ma'lumotlari:${NC}"
echo -e "${GREEN}Project: $PROJECT_DIR${NC}"
echo -e "${GREEN}Service: $SERVICE_NAME (service: $USE_SERVICE)${NC}"

echo -e "\n${BLUE}🔍 Monitoring Buyruqlari:${NC}"
if [ "$USE_SERVICE" = true ]; then
    echo -e "${YELLOW}  sudo systemctl status $SERVICE_NAME${NC}"
    echo -e "${YELLOW}  sudo journalctl -u $SERVICE_NAME -f${NC}"
else
    echo -e "${YELLOW}  ps aux | grep gunicorn${NC}"
    echo -e "${YELLOW}  tail -f $PROJECT_DIR/logs/gunicorn_error.log${NC}"
fi

echo -e "\n${BLUE}🌐 Test URL:${NC}"
echo -e "${YELLOW}  curl http://localhost:8000/api/menu/${NC}"
echo -e "${YELLOW}  https://tokyokafe.uz/api/menu/${NC}"

echo -e "\n${GREEN}Restart muvaffaqiyatli tugadi!${NC} 🚀"

