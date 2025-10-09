// PM2 Ecosystem Config - Tokyo Kafe
// ===================================
// Frontend (Next.js) uchun PM2 konfiguratsiyasi

module.exports = {
  apps: [
    {
      name: 'tokyo-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/u1234567/public_html/frontend',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'https://tokyokafe.uz',
      },
      error_file: '/home/u1234567/public_html/logs/frontend-error.log',
      out_file: '/home/u1234567/public_html/logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      
      // Auto restart settings
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      
      // Monitoring
      listen_timeout: 10000,
      kill_timeout: 5000,
    }
  ],
};

// Ishlatish:
// ==========
// pm2 start pm2_ecosystem.config.js
// pm2 save
// pm2 startup (server restart bo'lganda auto start)
// 
// Status:
// pm2 status
// pm2 logs tokyo-frontend
// pm2 monit
// 
// Restart:
// pm2 restart tokyo-frontend
// pm2 reload tokyo-frontend  # Zero-downtime restart

