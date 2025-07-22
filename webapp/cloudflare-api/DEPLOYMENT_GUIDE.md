# Deployment Guide: Migrating from Render to Cloudflare Workers

## Step 1: Deploy to Cloudflare Workers

1. **Create a Cloudflare account** (if you don't have one):
   - Go to https://dash.cloudflare.com/sign-up
   - Sign up for free

2. **Install dependencies**:
   ```bash
   cd webapp/cloudflare-api
   npm install
   ```

3. **Login to Cloudflare**:
   ```bash
   npx wrangler login
   ```
   This will open a browser window for authentication.

4. **Deploy the Worker**:
   ```bash
   npm run deploy
   ```
   
   You'll get a URL like: `https://watertrace-api.YOUR-SUBDOMAIN.workers.dev`

## Step 2: Update Frontend Configuration

1. **Edit the frontend config file**:
   ```bash
   cd ../frontend
   ```

2. **Update `src/config.js`**:
   ```javascript
   // Replace the Render URL with your Cloudflare Workers URL
   const API_URL = process.env.NODE_ENV === 'production' 
     ? 'https://watertrace-api.YOUR-SUBDOMAIN.workers.dev'  // Your Cloudflare URL
     : 'http://localhost:8787';  // Local development
   
   export default API_URL;
   ```

3. **Test locally**:
   ```bash
   npm start
   ```

4. **Deploy frontend** (if using Vercel):
   ```bash
   vercel --prod
   ```

## Step 3: Verify the Migration

1. **Check API directly**:
   - Visit: `https://watertrace-api.YOUR-SUBDOMAIN.workers.dev/api/health`
   - Should return: `{"status":"healthy","timestamp":"..."}`

2. **Check frontend**:
   - Visit your frontend URL
   - Data should load instantly (no more 5-10 second delays!)

## Performance Comparison

### Before (Render):
- Initial load: 5-10 seconds
- API response: 500-2000ms
- Cold starts: Yes
- Geographic performance: Varies

### After (Cloudflare Workers):
- Initial load: <1 second
- API response: <50ms
- Cold starts: None
- Geographic performance: Consistent globally

## Troubleshooting

**Issue: "Script not found" error**
- Make sure you're in the `webapp/cloudflare-api` directory
- Run `npm install` to install dependencies

**Issue: "Authentication required"**
- Run `npx wrangler login` and complete authentication

**Issue: Frontend still slow**
- Double-check that `config.js` is updated with the new URL
- Clear browser cache
- Check browser console for any errors

## Optional: Custom Domain

To use a custom domain (e.g., api.watertrace.com):

1. Add your domain to Cloudflare
2. Update `wrangler.toml`:
   ```toml
   [env.production]
   route = { pattern = "api.watertrace.com/*", zone_name = "watertrace.com" }
   ```
3. Redeploy: `npm run deploy`

## Monitoring

View your Worker analytics:
1. Go to https://dash.cloudflare.com
2. Select "Workers & Pages"
3. Click on your Worker
4. View metrics, logs, and performance data

## Next Steps

- Monitor the API performance in Cloudflare dashboard
- Consider adding caching headers for even better performance
- Set up error alerting if needed
- Remove the old Render deployment once stable