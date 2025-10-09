#!/bin/bash

# TokyoKafe Beget Server Qayta Ishga Tushirish Skripti
# ====================================================

# Ranglar
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tokyo Kafe - Server Qayta Ishga Tushirish${NC}"
echo -e "${GREEN}========================================${NC}"

# To'xtatish
echo -e "\n${YELLOW}Step 1: Serverni to'xtatish...${NC}"
bash stop_beget.sh

echo -e "\n${YELLOW}3 soniya kutilmoqda...${NC}"
sleep 3

# Ishga tushirish
echo -e "\n${YELLOW}Step 2: Serverni ishga tushirish...${NC}"
bash start_beget.sh


