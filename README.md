# Living Lore Board - Backend Deployment Guide

## 📦 Deployment Package Contents

This folder contains all files necessary to deploy the Living Lore Board backend to production.

### Files Included:
- `app.py` - Main FastAPI application entry point
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template (copy to `.env` and fill in)
- `agents/` - LangChain agent modules (lore generation, memory management)
- `ml_pipeline/` - ML components (image generation, NLP extraction)
- `Dockerfile` - Container configuration for deployment
- `docker-compose.yml` - Multi-container orchestration (optional)
- `railway.json` - Railway.app deployment configuration
- `render.yaml` - Render.com deployment configuration
- `vercel.json` - Vercel deployment configuration
- `Procfile` - Heroku/generic PaaS configuration
- `gunicorn.conf.py` - Production WSGI server configuration
- `nginx.conf` - Nginx reverse proxy configuration (for VPS deployment)
- `deploy.sh` - Automated deployment script
- `health_check.py` - Health monitoring script

---

## 🚀 Deployment Options

### Option 1: Railway.app (Recommended - Easy & Free Tier)

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Set environment variables:
   ```bash
   railway variables set GROQ_API_KEY=your_key_here
   railway variables set GOOGLE_API_KEY=your_key_here
   railway variables set HF_TOKEN=your_token_here
   railway variables set HOST=0.0.0.0
   railway variables set PORT=8000
   ```

4. Deploy:
   ```bash
   railway up
   ```

### Option 2: Render.com (Simple with Auto-Deploy)

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in the Render dashboard
6. Deploy automatically on git push

### Option 3: Docker (Any Cloud Provider)

1. Build the image:
   ```bash
   docker build -t living-lore-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env living-lore-backend
   ```

3. Or use docker-compose:
   ```bash
   docker-compose up -d
   ```

### Option 4: VPS (DigitalOcean, AWS EC2, etc.)

1. SSH into your server
2. Clone/upload this folder
3. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your keys
   ```

5. Run with systemd (production):
   ```bash
   sudo cp living-lore-backend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable living-lore-backend
   sudo systemctl start living-lore-backend
   ```

6. Configure Nginx as reverse proxy:
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/living-lore-backend
   sudo ln -s /etc/nginx/sites-available/living-lore-backend /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 5: Vercel (Serverless)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Add environment variables via Vercel dashboard

---

## 🔐 Environment Variables Required

Copy `.env.example` to `.env` and fill in these values:

```env
# Groq API (Primary LLM Engine)
GROQ_API_KEY=your_groq_api_key

# Google Gemini API (Fallback)
GOOGLE_API_KEY=your_google_api_key

# Hugging Face Token (for image generation models)
HF_TOKEN=your_huggingface_token

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Getting API Keys:

1. **Groq API Key**: https://console.groq.com/keys
2. **Google Gemini API**: https://aistudio.google.com/app/apikey
3. **Hugging Face Token**: https://huggingface.co/settings/tokens

---

## 📋 Pre-Deployment Checklist

- [ ] All environment variables set
- [ ] Dependencies installed and tested locally
- [ ] API keys are valid and have quota
- [ ] CORS origins updated for production domain
- [ ] Health endpoint (`/health`) returns 200 OK
- [ ] Test all three endpoints:
  - POST `/generate-lore`
  - POST `/generate-avatar`
  - POST `/extract-entities`

---

## 🔍 Health Monitoring

After deployment, monitor your service:

```bash
# Check health endpoint
curl https://your-domain.com/health

# Run health check script
python health_check.py https://your-domain.com
```

---

## 🐛 Troubleshooting

### Issue: Port already in use
**Solution**: Change PORT in .env or kill existing process

### Issue: Import errors
**Solution**: Ensure all dependencies in requirements.txt are installed

### Issue: API key errors
**Solution**: Verify keys are set correctly in environment variables

### Issue: CORS errors
**Solution**: Update `origins` list in `app.py` to include your frontend domain

### Issue: Image generation fails
**Solution**: Uses Pollinations AI (free, no auth), should work by default

---

## 📊 Performance Considerations

- **Memory**: Minimum 512MB RAM recommended
- **CPU**: 1 vCPU sufficient for light traffic
- **Storage**: ~500MB for dependencies
- **Network**: Image generation requires stable internet

---

## 🔒 Security Best Practices

1. Never commit `.env` file to version control
2. Use secrets management for production (AWS Secrets Manager, Railway Variables, etc.)
3. Enable HTTPS/SSL certificates (Let's Encrypt recommended)
4. Implement rate limiting for API endpoints
5. Set up monitoring and alerting
6. Regular dependency updates: `pip install --upgrade -r requirements.txt`

---

## 📈 Scaling Recommendations

For high traffic:
1. Use a production WSGI server (Gunicorn with workers)
2. Implement Redis caching for repeated lore generations
3. Consider CDN for generated images
4. Set up load balancing with multiple instances
5. Database integration for persistent memory (currently in-memory)

---

## 📞 Support

For issues or questions:
- Check logs: `railway logs` or `docker logs living-lore-backend`
- Review API documentation at `/docs` endpoint (FastAPI auto-generates Swagger UI)
- Test endpoints individually with Postman or curl

---

**Last Updated**: 2026-07-18
**Backend Version**: 0.1.0
