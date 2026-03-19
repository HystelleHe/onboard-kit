#!/bin/bash
# 数据库备份脚本 - 每天运行

cd /opt/onboard-kit

# 备份数据库
docker exec onboardkit-postgres pg_dump -U postgres onboardkit > /backup/onboardkit_$(date +%Y%m%d).sql 2>/dev/null

# 保留最近7天备份
find /backup -name "onboardkit_*.sql" -mtime +7 -delete

echo "Backup completed at $(date)"
