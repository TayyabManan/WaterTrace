# DEPRECATED - Flask Backend

This Flask backend has been migrated to Cloudflare Workers for better performance.

## Migration Details
- **Migration Date**: January 2025
- **New API**: https://watertrace-api.watertrace.workers.dev
- **Performance Improvement**: 200x faster response times
- **Technology**: Cloudflare Workers with TypeScript

## New Backend Location
The new API implementation is located at:
```
webapp/cloudflare-api/
```

## Why We Migrated
1. **Performance**: Eliminated 5-10 second cold starts
2. **Global Distribution**: API runs at edge locations worldwide
3. **Cost**: More cost-effective for our usage patterns
4. **Reliability**: 99.99% uptime SLA

## Data Migration
All data has been embedded directly in the Cloudflare Worker for zero-latency access:
- GRACE data (2002-2017): 163 data points
- GLDAS data (2018-2024): 84 data points
- District data: 33 districts across 4 provinces

## For Historical Reference
This directory is kept for historical reference only. Do not use for production.