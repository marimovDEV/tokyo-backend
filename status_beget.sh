#!/bin/bash

# TokyoKafe Beget Server Status Tekshirish
# =========================================

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Tokyo Kafe - Server Status${NC}"
echo -e "${BLUE}========================================${NC}"

# Beget server yo'llari
BEGET_USER="u1234567"  # O'zingizning Beget username
BEGET_HOME="/home/$BEGET_USER"
PROJECT_DIR="$BEGET_HOME/public_html/backend"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"
LOGS_DIR="$PROJECT_DIR/logs"

echo -e "\n${YELLOW}[1] PID faylni tekshirish...${NC}"
if [ -f "$GUNICORN_PID" ]; then
    PID=$(cat $GUNICORN_PID)
    echo -e "${GREEN}✅ PID fayl topildi: $GUNICORN_PID${NC}"
    echo -e "${GREEN}   PID: $PID${NC}"
    
    if kill -0 $PID 2>/dev/null; then
        echo -e "${GREEN}✅ Jarayon ISHLAYAPTI (PID: $PID)${NC}"
    else
        echo -e "${RED}❌ Jarayon ISHLAMAYAPTI (PID fayl mavjud, lekin jarayon yo'q)${NC}"
    fi
else
    echo -e "${RED}❌ PID fayl topilmadi${NC}"
fi

echo -e "\n${YELLOW}[2] Barcha Gunicorn jarayonlarni tekshirish...${NC}"
GUNICORN_PIDS=$(ps aux | grep 'gunicorn.*tokyo' | grep -v grep)

if [ ! -z "$GUNICORN_PIDS" ]; then
    echo -e "${GREEN}✅ Gunicorn jarayonlar topildi:${NC}"
    echo "$GUNICORN_PIDS" | while read line; do
        echo -e "${GREEN}   → $line${NC}"
    done
else
    echo -e "${RED}❌ Gunicorn jarayonlar topilmadi${NC}"
fi

echo -e "\n${YELLOW}[3] Port 8000 tekshirish...${NC}"
PORT_CHECK=$(netstat -tuln 2>/dev/null | grep ':8000' || ss -tuln 2>/dev/null | grep ':8000')
if [ ! -z "$PORT_CHECK" ]; then
    echo -e "${GREEN}✅ Port 8000 band (server ishlayapti)${NC}"
    echo -e "${GREEN}   $PORT_CHECK${NC}"
else
    echo -e "${RED}❌ Port 8000 bo'sh${NC}"
fi

echo -e "\n${YELLOW}[4] So'nggi error loglar (oxirgi 10 qator)...${NC}"
if [ -f "$LOGS_DIR/gunicorn_error.log" ]; then
    echo -e "${BLUE}----------------------------------------${NC}"
    tail -10 $LOGS_DIR/gunicorn_error.log
    echo -e "${BLUE}----------------------------------------${NC}"
else
    echo -e "${RED}❌ Error log fayli topilmadi${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Server Status Tugadi${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${YELLOW}To'liq loglarni ko'rish:${NC}"
echo -e "  ${GREEN}tail -f $LOGS_DIR/gunicorn_error.log${NC}"
echo -e "  ${GREEN}tail -f $LOGS_DIR/gunicorn_access.log${NC}"


