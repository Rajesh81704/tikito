# Nginx Configuration for Tikito API

This directory contains the nginx reverse proxy configuration for the Tikito API.

## File: tikito-api.conf

This configuration:
- Listens on port 80 for `api.tikito.in`
- Proxies requests to the FastAPI application running on `localhost:8000`
- Includes WebSocket support
- Has health check endpoint at `/health`

## Deployment

The nginx configuration is automatically deployed via GitHub Actions when changes are pushed to the main branch.

The deployment workflow:
1. Checks if nginx config has changed
2. If changed, copies it to `/etc/nginx/conf.d/tikito-api.conf`
3. Tests nginx configuration
4. Reloads nginx if test passes

## Manual Deployment

If you need to manually update the nginx configuration on the VPS:

```bash
# SSH into VPS
ssh root@213.210.21.236

# Navigate to project directory
cd /opt/tikito

# Copy the configuration
sudo cp nginx/tikito-api.conf /etc/nginx/conf.d/tikito-api.conf

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

## SSL Certificate

SSL is managed by Let's Encrypt via Certbot. The certificate is automatically added to this configuration file on the server.

To renew the certificate (automatic renewal is already configured):
```bash
sudo certbot renew
```

## Important Notes

1. **Never commit SSL certificate files** - They are managed by Certbot on the server
2. **The base config (without SSL)** is stored in git
3. **Certbot modifies the server config** to add SSL configuration automatically
4. **GitHub Actions preserves the SSL configuration** when updating

## Troubleshooting

### Check nginx status
```bash
sudo systemctl status nginx
```

### Check nginx logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Test configuration
```bash
sudo nginx -t
```

### Reload after changes
```bash
sudo systemctl reload nginx
```

### Check if SSL certificate is valid
```bash
sudo certbot certificates
```
