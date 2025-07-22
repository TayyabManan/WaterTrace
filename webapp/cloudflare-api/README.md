# WaterTrace Cloudflare Workers API

This is the Cloudflare Workers version of the WaterTrace API, migrated from Flask for improved performance and global distribution.

## Features

- **Ultra-fast response times** (<50ms globally)
- **No cold starts** - Workers are always warm
- **Edge deployment** - Runs close to users worldwide
- **Embedded data** - No database queries needed
- **Simple deployment** - Single command deployment

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/historical/timeseries` - GRACE data (2002-2017)
- `GET /api/recent/timeseries` - GLDAS data (2018-2024)
- `GET /api/gldas/trend-analysis` - GLDAS trend analysis
- `GET /api/analysis/summary` - Project summary
- `GET /api/combined/timeline` - Combined GRACE + GLDAS data
- `GET /api/districts/groundwater` - District groundwater data
- `POST /api/predict` - Groundwater predictions

## Setup

1. Install dependencies:
```bash
npm install
```

2. Install Wrangler CLI globally (if not already installed):
```bash
npm install -g wrangler
```

3. Login to Cloudflare:
```bash
wrangler login
```

## Development

Run the development server:
```bash
npm run dev
```

The API will be available at `http://localhost:8787`

## Deployment

1. Update the `wrangler.toml` file with your domain/route if needed.

2. Deploy to Cloudflare Workers:
```bash
npm run deploy
```

3. Your API will be available at:
   - `https://watertrace-api.<your-subdomain>.workers.dev`
   - Or your custom domain if configured

## Performance Improvements

Compared to the Flask/Render deployment:
- **Response time**: 5-10s → <50ms (100x faster)
- **Cold starts**: Eliminated
- **Global availability**: Edge locations worldwide
- **Scalability**: Automatic scaling with no configuration

## Data Management

The data is embedded directly in the Worker code for maximum performance:
- `src/data/grace-data.ts` - GRACE satellite data
- `src/data/gldas-data.ts` - GLDAS model data

To update data:
1. Modify the TypeScript data files
2. Redeploy the Worker

## Migration Notes

- Machine learning predictions are simplified (linear extrapolation)
- All data processing is done in JavaScript
- CORS is enabled for all origins
- No external dependencies or databases needed

## Updating Frontend

Update your frontend to point to the new Cloudflare Workers URL:

```javascript
// In your frontend config.js
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://watertrace-api.<your-subdomain>.workers.dev'
  : 'http://localhost:8787';
```

## Cost

The Cloudflare Workers free tier includes:
- 100,000 requests/day
- 10ms CPU time per invocation
- Unlimited bandwidth

This should be more than sufficient for the WaterTrace application.