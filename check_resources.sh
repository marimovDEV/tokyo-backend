#!/bin/bash

# Tokyo Kafe - Server Resources Monitor
# ======================================
# Server resurslarini tekshirish va monitoring

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Tokyo Kafe - Server Resources Monitor        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

# 1. CPU Usage
echo -e "\n${YELLOW}[1] CPU Usage:${NC}"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')
echo -e "${GREEN}CPU: $CPU_USAGE${NC}"

# 2. Memory Usage
echo -e "\n${YELLOW}[2] Memory Usage:${NC}"
free -h
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo -e "${RED}⚠️  RAM 80% dan ko'p ishlatilgan!${NC}"
else
    echo -e "${GREEN}✅ RAM normal${NC}"
fi

# 3. Disk Usage
echo -e "\n${YELLOW}[3] Disk Usage:${NC}"
df -h | grep -E '^/dev/'
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo -e "${RED}⚠️  Disk 80% dan ko'p to'lgan!${NC}"
else
    echo -e "${GREEN}✅ Disk normal${NC}"
fi

# 4. Running Processes
echo -e "\n${YELLOW}[4] Tokyo Kafe Processes:${NC}"

# Gunicorn (Backend)
echo -e "${BLUE}Backend (Gunicorn):${NC}"
GUNICORN_COUNT=$(ps aux | grep -c '[g]unicorn')
if [ $GUNICORN_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ $GUNICORN_COUNT ta Gunicorn jarayon ishlayapti${NC}"
    ps aux | grep '[g]unicorn' | awk '{print "  PID: "$2" | CPU: "$3"% | RAM: "$4"% | "$11}'
else
    echo -e "${RED}❌ Gunicorn ishlamayapti!${NC}"
fi

# Node.js (Frontend)
echo -e "\n${BLUE}Frontend (Node.js):${NC}"
NODE_COUNT=$(ps aux | grep -c '[n]ode.*next')
if [ $NODE_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ $NODE_COUNT ta Node.js jarayon ishlayapti${NC}"
    ps aux | grep '[n]ode.*next' | awk '{print "  PID: "$2" | CPU: "$3"% | RAM: "$4"% | "$11}'
else
    echo -e "${RED}❌ Node.js ishlamayapti!${NC}"
fi

# 5. Network Connections
echo -e "\n${YELLOW}[5] Network Connections:${NC}"
PORT_8000=$(netstat -tuln 2>/dev/null | grep ':8000' || ss -tuln 2>/dev/null | grep ':8000')
PORT_3000=$(netstat -tuln 2>/dev/null | grep ':3000' || ss -tuln 2>/dev/null | grep ':3000')

if [ ! -z "$PORT_8000" ]; then
    echo -e "${GREEN}✅ Port 8000 (Backend) ishlayapti${NC}"
else
    echo -e "${RED}❌ Port 8000 (Backend) band emas!${NC}"
fi

if [ ! -z "$PORT_3000" ]; then
    echo -e "${GREEN}✅ Port 3000 (Frontend) ishlayapti${NC}"
else
    echo -e "${RED}❌ Port 3000 (Frontend) band emas!${NC}"
fi

# 6. Recent Errors
echo -e "\n${YELLOW}[6] Recent Backend Errors (so'nggi 5 ta):${NC}"
BACKEND_LOG="/home/u1234567/public_html/backend/logs/gunicorn_error.log"
if [ -f "$BACKEND_LOG" ]; then
    tail -5 $BACKEND_LOG | grep -i error || echo -e "${GREEN}✅ Hech qanday error yo'q${NC}"
else
    echo -e "${YELLOW}Log fayli topilmadi${NC}"
fi

echo -e "\n${YELLOW}[7] Recent Frontend Errors (so'nggi 5 ta):${NC}"
FRONTEND_LOG="/home/u1234567/public_html/logs/frontend-error.log"
if [ -f "$FRONTEND_LOG" ]; then
    tail -5 $FRONTEND_LOG | grep -i error || echo -e "${GREEN}✅ Hech qanday error yo'q${NC}"
else
    echo -e "${YELLOW}Log fayli topilmadi${NC}"
fi

# 7. Load Average
echo -e "\n${YELLOW}[8] Load Average:${NC}"
uptime

# 8. Open Files
echo -e "\n${YELLOW}[9] Open Files Count:${NC}"
OPEN_FILES=$(lsof 2>/dev/null | wc -l)
echo -e "${GREEN}Ochiq fayllar: $OPEN_FILES${NC}"

# 9. Recommendations
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  TAVSIYALAR                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo -e "${RED}• RAM 80% dan ko'p! Gunicorn worker sonini kamaytiring${NC}"
fi

if [ $DISK_USAGE -gt 80 ]; then
    echo -e "${RED}• Disk 80% dan ko'p! Eski loglarni tozalang${NC}"
fi

if [ $GUNICORN_COUNT -eq 0 ]; then
    echo -e "${RED}• Backend ishlamayapti! bash start_beget.sh ishga tushiring${NC}"
fi

if [ $NODE_COUNT -eq 0 ]; then
    echo -e "${RED}• Frontend ishlamayapti! pm2 start qiling${NC}"
fi

echo -e "\n${GREEN}✅ Monitoring tugadi!${NC}"

