#!/bin/bash

# TokyoKafe Beget Server Ishga Tushirish Skripti
# ================================================

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tokyo Kafe - Beget Server Ishga Tushirish${NC}"
echo -e "${GREEN}========================================${NC}"

# Beget server yo'llari (o'zingiznikini kiriting)
BEGET_USER="u1234567"  # O'zingizning Beget username
BEGET_HOME="/home/$BEGET_USER"
PROJECT_DIR="$BEGET_HOME/public_html/backend"
VENV_DIR="$PROJECT_DIR/venv"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"
LOGS_DIR="$PROJECT_DIR/logs"

echo -e "\n${YELLOW}[1/6]${NC} Loyiha papkasiga o'tish..."
cd $PROJECT_DIR || {
    echo -e "${RED}❌ Xato: Loyiha papkasi topilmadi: $PROJECT_DIR${NC}"
    exit 1
}

echo -e "${GREEN}✅ Hozirgi papka: $(pwd)${NC}"

echo -e "\n${YELLOW}[2/6]${NC} Virtual environment aktivlashtirish..."
if [ -d "$VENV_DIR" ]; then
    source $VENV_DIR/bin/activate
    echo -e "${GREEN}✅ Virtual environment aktivlashtirildi${NC}"
else
    echo -e "${RED}❌ Virtual environment topilmadi: $VENV_DIR${NC}"
    echo -e "${YELLOW}Virtual environment yaratish: python3 -m venv $VENV_DIR${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[3/6]${NC} Log papkalarini tekshirish..."
mkdir -p $LOGS_DIR
echo -e "${GREEN}✅ Log papkalari tayyor${NC}"

echo -e "\n${YELLOW}[4/6]${NC} Eski Gunicorn jarayonlarini to'xtatish..."
if [ -f "$GUNICORN_PID" ]; then
    OLD_PID=$(cat $GUNICORN_PID)
    if kill -0 $OLD_PID 2>/dev/null; then
        echo -e "${YELLOW}Eski jarayon topildi (PID: $OLD_PID), to'xtatilmoqda...${NC}"
        kill $OLD_PID
        sleep 2
        if kill -0 $OLD_PID 2>/dev/null; then
            echo -e "${YELLOW}Majburan to'xtatilmoqda...${NC}"
            kill -9 $OLD_PID
        fi
        echo -e "${GREEN}✅ Eski jarayon to'xtatildi${NC}"
    else
        echo -e "${YELLOW}PID fayl mavjud, lekin jarayon ishlamayapti${NC}"
        rm -f $GUNICORN_PID
    fi
else
    echo -e "${GREEN}✅ Eski jarayonlar yo'q${NC}"
fi

# Barcha gunicorn jarayonlarini topish va to'xtatish
GUNICORN_PIDS=$(ps aux | grep 'gunicorn.*tokyo_restaurant' | grep -v grep | awk '{print $2}')
if [ ! -z "$GUNICORN_PIDS" ]; then
    echo -e "${YELLOW}Qolgan Gunicorn jarayonlarni to'xtatish...${NC}"
    echo "$GUNICORN_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
    echo -e "${GREEN}✅ Barcha Gunicorn jarayonlar to'xtatildi${NC}"
fi

echo -e "\n${YELLOW}[5/6]${NC} Django migratsiyalarni tekshirish..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migratsiyalar muvaffaqiyatli bajarildi${NC}"
else
    echo -e "${RED}❌ Migratsiya xatosi${NC}"
fi

echo -e "\n${YELLOW}[5.5/6]${NC} Statik fayllarni yig'ish..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Statik fayllar yig'ildi${NC}"
else
    echo -e "${YELLOW}⚠️  Statik fayllar yig'ishda xatolik${NC}"
fi

echo -e "\n${YELLOW}[6/6]${NC} Gunicorn serverini ishga tushirish..."

# Gunicorn ishga tushirish (daemon mode)
gunicorn restaurant_api.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 30 \
    --access-logfile $LOGS_DIR/gunicorn_access.log \
    --error-logfile $LOGS_DIR/gunicorn_error.log \
    --pid $GUNICORN_PID \
    --daemon

sleep 2

# Tekshirish
if [ -f "$GUNICORN_PID" ]; then
    NEW_PID=$(cat $GUNICORN_PID)
    if kill -0 $NEW_PID 2>/dev/null; then
        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}✅ SERVER MUVAFFAQIYATLI ISHGA TUSHDI!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}PID: $NEW_PID${NC}"
        echo -e "${GREEN}Port: 8000${NC}"
        echo -e "${GREEN}Access Log: $LOGS_DIR/gunicorn_access.log${NC}"
        echo -e "${GREEN}Error Log: $LOGS_DIR/gunicorn_error.log${NC}"
        echo -e "\n${YELLOW}Serverni to'xtatish uchun: bash stop_beget.sh${NC}"
        echo -e "${YELLOW}Loglarni ko'rish uchun: tail -f $LOGS_DIR/gunicorn_error.log${NC}"
    else
        echo -e "${RED}❌ Server ishga tushmadi! Loglarni tekshiring:${NC}"
        echo -e "${RED}tail -50 $LOGS_DIR/gunicorn_error.log${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ PID fayl yaratilmadi. Server ishga tushmagan bo'lishi mumkin.${NC}"
    exit 1
fi


