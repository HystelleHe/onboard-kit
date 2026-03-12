# OnboardKit 部署清单

## 部署前准备

### 1. 服务器要求
- [ ] CPU: 4核或以上
- [ ] 内存: 8GB或以上
- [ ] 硬盘: 50GB SSD或以上
- [ ] 操作系统: Ubuntu 20.04+ / CentOS 8+
- [ ] Docker: 20.10+
- [ ] Docker Compose: 2.0+

### 2. 域名和SSL
- [ ] 域名已备案（中国大陆）
- [ ] DNS记录已配置
  - A记录: yourdomain.com -> 服务器IP
  - A记录: api.yourdomain.com -> 服务器IP
- [ ] SSL证书已准备（Let's Encrypt 或购买）

### 3. 环境变量配置
- [ ] 复制 `backend/.env.example` 到 `backend/.env`
- [ ] 修改以下关键配置:
  - [ ] `SECRET_KEY`: 至少32字符的随机字符串
  - [ ] `POSTGRES_PASSWORD`: 强密码（16+字符）
  - [ ] `REDIS_PASSWORD`: 强密码
  - [ ] `BACKEND_CORS_ORIGINS`: 生产域名
- [ ] 复制 `frontend/.env.example` 到 `frontend/.env.production`
- [ ] 修改 `VITE_API_BASE_URL` 为生产API地址

## 部署步骤

### 步骤1: 服务器初始化

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 重新登录以应用Docker组权限
logout
```

### 步骤2: 克隆项目

```bash
# 创建项目目录
mkdir -p /opt/onboardkit
cd /opt/onboardkit

# 克隆代码
git clone https://github.com/yourusername/onboard-kit.git .

# 或使用SSH
git clone git@github.com:yourusername/onboard-kit.git .
```

### 步骤3: 配置环境

```bash
# 1. 配置后端环境变量
cp backend/.env.example backend/.env
nano backend/.env

# 2. 生成随机密钥
openssl rand -hex 32

# 3. 配置前端环境变量
cp frontend/.env.example frontend/.env.production
nano frontend/.env.production
```

### 步骤4: 配置SSL (可选但推荐)

#### 使用 Let's Encrypt

```bash
# 1. 安装 Certbot
sudo apt install certbot

# 2. 生成证书
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# 3. 创建SSL目录
mkdir -p ssl

# 4. 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chown -R $USER:$USER ssl/

# 5. 设置自动续期
sudo crontab -e
# 添加: 0 0 * * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /opt/onboardkit/ssl/
```

#### 使用自签名证书 (仅测试)

```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/CN=yourdomain.com"
```

### 步骤5: 部署服务

```bash
# 1. 使用部署脚本
./deploy.sh

# 2. 或手动部署
docker-compose -f docker-compose.prod.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 4. 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 步骤6: 初始化数据库

```bash
# 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 验证数据库
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d onboardkit -c "\dt"
```

### 步骤7: 配置防火墙

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 步骤8: 配置 Nginx (如果不使用Docker Nginx)

```bash
# 1. 安装 Nginx
sudo apt install nginx

# 2. 创建配置
sudo nano /etc/nginx/sites-available/onboardkit

# 3. 复制以下配置:
# (见 docs/nginx-example.conf)

# 4. 启用站点
sudo ln -s /etc/nginx/sites-available/onboardkit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 部署后验证

### 健康检查

- [ ] 前端访问: https://yourdomain.com
- [ ] 后端健康: https://api.yourdomain.com/health
- [ ] API文档: https://api.yourdomain.com/docs
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 创建引导功能正常
- [ ] 页面分析功能正常
- [ ] 代码生成功能正常

### 性能测试

```bash
# 使用 Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/

# 查看响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/
```

## 监控和维护

### 1. 日志管理

```bash
# 查看所有日志
docker-compose -f docker-compose.prod.yml logs

# 实时日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 清理旧日志
docker-compose -f docker-compose.prod.yml logs --tail=100 > logs.txt
```

### 2. 数据库备份

```bash
# 创建备份脚本
cat > /opt/onboardkit/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/onboardkit/backups"
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose -f /opt/onboardkit/docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres onboardkit | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 删除7天前的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF

chmod +x /opt/onboardkit/backup.sh

# 添加定时任务
crontab -e
# 添加: 0 2 * * * /opt/onboardkit/backup.sh
```

### 3. 系统监控

```bash
# 安装监控工具
sudo apt install htop iotop

# Docker资源使用
docker stats

# 磁盘使用
df -h
du -sh /var/lib/docker
```

### 4. 更新部署

```bash
cd /opt/onboardkit

# 1. 备份数据库
./backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建并部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 4. 运行迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 5. 验证
docker-compose -f docker-compose.prod.yml ps
```

## 故障排查

### 容器无法启动

```bash
# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 数据库连接问题

```bash
# 测试数据库连接
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres

# 检查环境变量
docker-compose -f docker-compose.prod.yml exec backend env | grep POSTGRES
```

### 内存不足

```bash
# 清理Docker镜像和容器
docker system prune -a

# 查看内存使用
free -h
docker stats --no-stream
```

## 安全加固

- [ ] 修改SSH端口
- [ ] 禁用root登录
- [ ] 启用fail2ban
- [ ] 配置安全组规则
- [ ] 定期更新系统
- [ ] 启用Docker安全扫描
- [ ] 配置日志审计

## 回滚方案

```bash
# 1. 切换到上一个版本
git checkout <previous-commit>

# 2. 回滚数据库
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1

# 3. 重新部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. 恢复数据库备份（如果需要）
gunzip < backups/db_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T postgres \
psql -U postgres onboardkit
```

## 联系支持

如有问题，请联系:
- GitHub Issues: https://github.com/yourusername/onboard-kit/issues
- 邮箱: hystelle1223@163.com
