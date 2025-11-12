#!/bin/bash

# TokyoKafe Beget Server To'xtatish Skripti
# ==========================================

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Tokyo Kafe - Beget Server To'xtatish${NC}"
echo -e "${YELLOW}========================================${NC}"

# Server yo'llari
PROJECT_DIR="/root/tokyo/backend"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"

echo -e "\n${YELLOW}[1/2]${NC} PID fayldan jarayonni to'xtatish..."
if [ -f "$GUNICORN_PID" ]; then
    PID=$(cat $GUNICORN_PID)
    if kill -0 $PID 2>/dev/null; then
        echo -e "${YELLOW}Jarayon topildi (PID: $PID), to'xtatilmoqda...${NC}"
        kill $PID
        sleep 2
        
        # Agar hali ham ishlayotgan bo'lsa, majburan to'xtatish
        if kill -0 $PID 2>/dev/null; then
            echo -e "${YELLOW}Majburan to'xtatilmoqda...${NC}"
            kill -9 $PID
            sleep 1
        fi
        
        rm -f $GUNICORN_PID
        echo -e "${GREEN}✅ Server to'xtatildi (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}PID fayl mavjud, lekin jarayon ishlamayapti${NC}"
        rm -f $GUNICORN_PID
        echo -e "${GREEN}✅ PID fayl o'chirildi${NC}"
    fi
else
    echo -e "${YELLOW}PID fayl topilmadi${NC}"
fi

echo -e "\n${YELLOW}[2/2]${NC} Qolgan Gunicorn jarayonlarni tekshirish..."
GUNICORN_PIDS=$(ps aux | grep 'gunicorn.*tokyo_restaurant' | grep -v grep | awk '{print $2}')

if [ ! -z "$GUNICORN_PIDS" ]; then
    echo -e "${YELLOW}Qolgan jarayonlar topildi:${NC}"
    echo "$GUNICORN_PIDS"
    echo -e "${YELLOW}To'xtatilmoqda...${NC}"
    echo "$GUNICORN_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
    echo -e "${GREEN}✅ Barcha Gunicorn jarayonlar to'xtatildi${NC}"
else
    echo -e "${GREEN}✅ Qolgan jarayonlar yo'q${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ BARCHA JARAYONLAR TO'XTATILDI${NC}"
echo -e "${GREEN}========================================${NC}"


