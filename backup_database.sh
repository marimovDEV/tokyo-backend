#!/bin/bash

# Database Backup Script for TokyoKafe
# =====================================

# Ranglar
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tokyo Kafe - Database Backup${NC}"
echo -e "${GREEN}========================================${NC}"

# Beget server yo'llari
BEGET_USER="u1234567"  # O'zingizning Beget username
BEGET_HOME="/home/$BEGET_USER"
PROJECT_DIR="$BEGET_HOME/public_html/backend"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "\n${YELLOW}[1/4]${NC} Backup papkasini yaratish..."
mkdir -p $BACKUP_DIR
echo -e "${GREEN}✅ Backup papkasi: $BACKUP_DIR${NC}"

echo -e "\n${YELLOW}[2/4]${NC} Database backup olish..."
cd $PROJECT_DIR || {
    echo -e "${RED}❌ Xato: Loyiha papkasi topilmadi: $PROJECT_DIR${NC}"
    exit 1
}

# Virtual environment aktivlashtirish
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment topilmadi${NC}"
    exit 1
fi

# SQLite database backup (agar SQLite ishlatilsa)
if [ -f "db.sqlite3" ]; then
    BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sqlite3"
    cp db.sqlite3 $BACKUP_FILE
    echo -e "${GREEN}✅ SQLite database backup: $BACKUP_FILE${NC}"
    
    # JSON export ham yaratish
    JSON_BACKUP="$BACKUP_DIR/data_backup_${TIMESTAMP}.json"
    python manage.py dumpdata --indent 2 > $JSON_BACKUP
    echo -e "${GREEN}✅ JSON backup: $JSON_BACKUP${NC}"
fi

# PostgreSQL backup (agar PostgreSQL ishlatilsa)
# PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/pg_backup_${TIMESTAMP}.sql

echo -e "\n${YELLOW}[3/4]${NC} Media fayllarni backup qilish..."
if [ -d "media" ]; then
    MEDIA_BACKUP="$BACKUP_DIR/media_backup_${TIMESTAMP}.tar.gz"
    tar -czf $MEDIA_BACKUP media/
    echo -e "${GREEN}✅ Media backup: $MEDIA_BACKUP${NC}"
fi

echo -e "\n${YELLOW}[4/4]${NC} Backup hajmini ko'rsatish..."
du -sh $BACKUP_DIR/*${TIMESTAMP}* 2>/dev/null | while read size file; do
    echo -e "${GREEN}  $file: $size${NC}"
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ BACKUP MUVAFFAQIYATLI YAKUNLANDI!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Backup papkasi: $BACKUP_DIR${NC}"
echo -e "${YELLOW}Timestamp: $TIMESTAMP${NC}"

# Eski backup'larni o'chirish (30 kundan eski)
echo -e "\n${YELLOW}Eski backup'larni tozalash (30 kundan eski)...${NC}"
find $BACKUP_DIR -type f -mtime +30 -delete
echo -e "${GREEN}✅ Eski backup'lar tozalandi${NC}"

