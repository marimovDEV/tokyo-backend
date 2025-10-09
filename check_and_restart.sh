#!/bin/bash

# Tokyo Kafe - Auto Check and Restart
# Cron job uchun: har 5 daqiqada tekshirish va kerak bo'lsa qayta ishga tushirish
# */5 * * * * cd /home/u1234567/public_html/backend && bash check_and_restart.sh

BEGET_USER="u1234567"  # O'zingizning username
BEGET_HOME="/home/$BEGET_USER"
PROJECT_DIR="$BEGET_HOME/public_html/backend"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"

# PID faylni tekshirish
if [ -f "$GUNICORN_PID" ]; then
    PID=$(cat $GUNICORN_PID)
    
    # Jarayon ishlayaptimi tekshirish
    if kill -0 $PID 2>/dev/null; then
        # Server ishlayapti, hech narsa qilmaymiz
        exit 0
    else
        # Server ishlamayapti, qayta ishga tushiramiz
        echo "$(date): Server ishlamayapti, qayta ishga tushirilmoqda..." >> $PROJECT_DIR/logs/auto_restart.log
        cd $PROJECT_DIR
        bash restart_beget.sh >> $PROJECT_DIR/logs/auto_restart.log 2>&1
    fi
else
    # PID fayl yo'q, server ishlamayapti
    echo "$(date): PID fayl topilmadi, server ishga tushirilmoqda..." >> $PROJECT_DIR/logs/auto_restart.log
    cd $PROJECT_DIR
    bash start_beget.sh >> $PROJECT_DIR/logs/auto_restart.log 2>&1
fi


