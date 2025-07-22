// Simple test script for the WaterTrace API
// Run with: node test-api.js

const API_URL = 'http://localhost:8787';

async function testEndpoint(path, method = 'GET', body = null) {
  console.log(`\nTesting ${method} ${path}`);
  console.log('-'.repeat(50));
  
  try {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_URL}${path}`, options);
    const data = await response.json();
    
    console.log(`Status: ${response.status}`);
    console.log('Response:', JSON.stringify(data, null, 2).substring(0, 500) + '...');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

async function runTests() {
  console.log('Starting WaterTrace API tests...\n');
  
  // Test all endpoints
  await testEndpoint('/');
  await testEndpoint('/api/health');
  await testEndpoint('/api/historical/timeseries');
  await testEndpoint('/api/recent/timeseries');
  await testEndpoint('/api/gldas/trend-analysis');
  await testEndpoint('/api/analysis/summary');
  await testEndpoint('/api/combined/timeline');
  await testEndpoint('/api/districts/groundwater');
  await testEndpoint('/api/predict', 'POST', { years: 5 });
  
  console.log('\nTests completed!');
}

// Check if fetch is available (Node 18+)
if (typeof fetch === 'undefined') {
  console.error('This script requires Node.js 18+ with native fetch support');
  console.error('Or install node-fetch: npm install node-fetch');
  process.exit(1);
}

runTests();