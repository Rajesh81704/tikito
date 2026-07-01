# Tikito Backend - Deployment Setup Summary

## ✅ What's Been Configured

### 1. VPS Setup (213.210.21.236)
- **Location**: `/opt/tikito`
- **Backend**: FastAPI running on port 8000
- **Service**: Managed by systemd (`tikito.service`)
- **Python**: Running in virtual environment (`venv/`)

### 2. Nginx Reverse Proxy
- **Config**: `/etc/nginx/conf.d/tikito-api.conf`
- **Domain**: api.tikito.in
- **Proxies**: Port 80/443 → localhost:8000
- **SSL**: Let's Encrypt (expires: 2026-09-29)
- **Auto-renewal**: Configured via certbot

### 3. Git Repository Integration
- **Nginx config**: Now tracked in `nginx/tikito-api.conf`
- **GitHub Actions**: Auto-deploys on push to main branch
- **Workflow**: 
  - Pulls latest code
  - Updates nginx if config changed
  - Installs dependencies
  - Restarts tikito service

### 4. SSL/HTTPS
- **Certificate**: Let's Encrypt
- **Auto-redirect**: HTTP → HTTPS
- **Status**: ✅ Active

## 🔧 How It Works

### Deployment Flow
1. Developer pushes code to GitHub (main branch)
2. GitHub Action triggers automatically
3. Action SSHs into VPS
4. Pulls latest code from GitHub
5. Checks if nginx config changed
6. Updates nginx if needed
7. Installs/updates Python dependencies
8. Restarts tikito service
9. Backend is live with new code

### Nginx Configuration Persistence
- Base nginx config is stored in Git: `nginx/tikito-api.conf`
- SSL configuration added by Certbot (not in Git)
- GitHub Action intelligently updates only if changed
- SSL settings are preserved during updates

## 📋 Important Commands

### On VPS (SSH: root@213.210.21.236)

```bash
# Check backend status
systemctl status tikito

# Restart backend
systemctl restart tikito

# View backend logs
journalctl -u tikito -f

# Check nginx status
systemctl status nginx

# Test nginx config
nginx -t

# Reload nginx
systemctl reload nginx

# View nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Check SSL certificate
certbot certificates

# Renew SSL certificate (auto-renews)
certbot renew
```

### Local Development

```bash
# Make code changes
git add .
git commit -m "your changes"
git push origin main

# GitHub Actions will automatically deploy to VPS
```

## ⚠️ Pending Action Required

**Update DNS in Cloudflare**

Currently `api.tikito.in` points to Cloudflare proxy IPs.
It needs to point to your VPS: **213.210.21.236**

1. Login to Cloudflare: https://dash.cloudflare.com/
2. Select `tikito.in` domain
3. Go to DNS settings
4. Update the `api` A record:
   - Type: A
   - Name: api
   - IPv4: 213.210.21.236
   - Proxy: OFF (gray cloud)
5. Save

After DNS update (5-10 min), access:
- https://api.tikito.in/docs
- https://api.tikito.in/health

## 🔐 GitHub Secrets Needed (For GitHub Actions)

Add these secrets in GitHub repository settings:
- `VPS_HOST`: 213.210.21.236
- `VPS_USERNAME`: root
- `VPS_SSH_KEY`: Your SSH private key
- `VPS_PORT`: 22
- `VPS_PROJECT_PATH`: /opt/tikito

## 📝 Recent Changes Deployed

1. **Phone number made optional** for user registration
   - Users can register with email only, phone only, or both
   - At least one is required
   - Database schema updated

2. **Nginx configuration** added to Git
   - Ensures config persists across deployments
   - Automatic sync via GitHub Actions

## 🧪 Testing

```bash
# Test locally via IP
curl http://213.210.21.236:8000/docs

# Test via domain (after DNS update)
curl https://api.tikito.in/docs
curl https://api.tikito.in/health

# Test API endpoint
curl https://api.tikito.in/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@email.com","password":"test","role":"user"}'
```

## 📚 Documentation Files

- `PHONE_OPTIONAL_CHANGES.md` - Details about phone optional feature
- `DNS_UPDATE_INSTRUCTIONS.md` - DNS configuration guide
- `nginx/README.md` - Nginx configuration guide
- `DEPLOYMENT_SETUP.md` - This file

## 🆘 Troubleshooting

### Backend not responding
```bash
ssh root@213.210.21.236
systemctl status tikito
journalctl -u tikito -n 50
```

### Nginx errors
```bash
ssh root@213.210.21.236
nginx -t
tail -f /var/log/nginx/error.log
```

### GitHub Actions failing
- Check: https://github.com/Rajesh81704/tikito/actions
- Verify GitHub secrets are set correctly
- Check VPS SSH access

### DNS not resolving
```bash
dig api.tikito.in +short
# Should return: 213.210.21.236
```
