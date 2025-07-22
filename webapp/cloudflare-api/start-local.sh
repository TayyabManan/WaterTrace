#!/bin/bash
echo "Starting Cloudflare Workers API locally..."
echo "Installing dependencies..."
npm install
echo ""
echo "Starting development server..."
echo "API will be available at http://localhost:8787"
echo ""
npx wrangler dev