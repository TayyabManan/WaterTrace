import { graceData } from './data/grace-data';
import { gldasData } from './data/gldas-data';

export interface Env {
  // Environment bindings
}

// CORS headers for all responses
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// Helper function to create JSON response with CORS
function jsonResponse(data: any, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders,
    },
  });
}

// Calculate statistics for data
function calculateStats(data: number[]) {
  const mean = data.reduce((a, b) => a + b, 0) / data.length;
  const min = Math.min(...data);
  const max = Math.max(...data);
  return { mean, min, max };
}

// Calculate trend (simple linear regression)
function calculateTrend(data: { date: string; value: number }[]) {
  const n = data.length;
  if (n === 0) return { slope: 0, intercept: 0 };
  
  // Convert dates to numeric values (days since first date)
  const firstDate = new Date(data[0].date).getTime();
  const x = data.map(d => (new Date(d.date).getTime() - firstDate) / (1000 * 60 * 60 * 24));
  const y = data.map(d => d.value);
  
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((acc, xi, i) => acc + xi * y[i], 0);
  const sumX2 = x.reduce((acc, xi) => acc + xi * xi, 0);
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  
  // Convert slope from per day to per year
  const annualTrend = slope * 365.25;
  
  return { slope: annualTrend, intercept };
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Route handling
    switch (path) {
      case '/':
        return jsonResponse({
          message: 'WaterTrace API - Cloudflare Workers Edition',
          version: '2.0',
          endpoints: [
            '/api/health',
            '/api/historical/timeseries',
            '/api/recent/timeseries',
            '/api/gldas/trend-analysis',
            '/api/analysis/summary',
            '/api/combined/timeline',
            '/api/districts/groundwater',
            '/api/predict'
          ]
        });

      case '/api/health':
        return jsonResponse({ status: 'healthy', timestamp: new Date().toISOString() });

      case '/api/historical/timeseries':
        // Return GRACE data
        const graceValues = graceData.map(d => d.groundwater_cm);
        const graceStats = calculateStats(graceValues);
        
        return jsonResponse({
          data: graceData,
          summary: {
            period: '2002-2017',
            data_source: 'GRACE satellite',
            total_records: graceData.length,
            statistics: graceStats,
            unit: 'cm'
          }
        });

      case '/api/recent/timeseries':
        // Return GLDAS data matching Flask API
        const gldasBaseline = gldasData.slice(0, 12).reduce((acc, d) => acc + d.groundwater_cm, 0) / 12;
        const gldasTimeseries = gldasData.map(d => ({
          date: d.date,
          groundwater_cm: d.groundwater_cm,
          data_source: 'GLDAS',
          groundwater_anomaly_cm: d.groundwater_cm - gldasBaseline
        }));
        
        return jsonResponse({
          success: true,
          data: gldasTimeseries,
          summary: {
            period: '2018-2024',
            data_source: 'GLDAS model',
            total_records: gldasData.length,
            baseline_value: gldasBaseline,
            unit: 'kg/m²'
          }
        });

      case '/api/gldas/trend-analysis':
        // Analyze GLDAS trends matching Flask API structure
        const baseline2018 = gldasData.filter(d => d.year === 2018).reduce((sum, d) => sum + d.groundwater_cm, 0) / 12;
        const currentValue = gldasData[gldasData.length - 1].groundwater_cm;
        const totalChange = currentValue - gldasData[0].groundwater_cm;
        
        // Calculate trend
        const gldasTrendData = gldasData.map(d => ({
          date: d.date,
          value: d.groundwater_cm
        }));
        
        const trend = calculateTrend(gldasTrendData);
        const annualChange = trend.slope;
        
        // Interpretation
        let interpretation = "Relatively stable - minimal change detected";
        if (annualChange < -2) {
          interpretation = "Declining trend - likely continued groundwater depletion";
        } else if (annualChange > 2) {
          interpretation = "Increasing trend - possible stabilization or recovery";
        }
        
        // Time series with anomalies
        const timeSeries = gldasData.map(d => ({
          date: d.date,
          absolute_value: d.groundwater_cm,
          anomaly: d.groundwater_cm - baseline2018,
          year: d.year
        }));
        
        return jsonResponse({
          success: true,
          analysis: {
            baseline_2018: baseline2018,
            current_value: currentValue,
            total_change: totalChange,
            annual_change: annualChange,
            monthly_change: annualChange / 12,
            interpretation: interpretation,
            trend_direction: annualChange > 0 ? 'increasing' : 'decreasing',
            comparison_note: 'GLDAS measures soil moisture, not direct groundwater. Positive values may indicate better water retention.'
          },
          time_series: timeSeries,
          metadata: {
            data_source: 'GLDAS V021',
            variable: 'Deep Soil Moisture (100-200cm)',
            units: 'kg/m²',
            period: '2018-01 to 2024-12'
          }
        });

      case '/api/analysis/summary':
        // Return project summary
        return jsonResponse({
          project: 'WaterTrace - Pakistan Groundwater Monitoring',
          description: 'Comprehensive groundwater depletion analysis using satellite data',
          key_findings: [
            'Pakistan lost 13.71 cm of groundwater from 2002-2017',
            'Annual depletion rate: -0.81 cm per year during GRACE period',
            'Recent GLDAS data shows slight improvement: +1.5 kg/m²/year',
            'Most affected region: Quetta with -15.3 cm depletion',
            'Critical districts: Lahore (-12.5 cm), Faisalabad (-10.8 cm)',
            '145 districts monitored across 4 provinces'
          ],
          data_sources: {
            historical: 'GRACE satellite (2002-2017)',
            recent: 'GLDAS model (2018-2024)'
          },
          coverage: '145 districts across Pakistan',
          study_area: {
            country: 'Pakistan',
            districts: 145,
            provinces: 4,
            area_km2: 881913
          },
          datasets: {
            historical: {
              name: 'GRACE',
              period: '2002-2017',
              data_points: 164,
              source: 'NASA/GFZ'
            },
            recent: {
              name: 'GLDAS',
              period: '2018-2024',
              data_points: 84,
              source: 'NASA LDAS'
            }
          }
        });

      case '/api/combined/timeline':
        // Combine GRACE and GLDAS data with EXACT same calculations as Flask
        const combinedData = [];
        
        // Add GRACE data (already in anomalies)
        graceData.forEach(d => {
          combinedData.push({
            date: d.date,
            value: d.groundwater_cm, // Already anomalies in cm
            source: 'GRACE',
            type: 'measured_anomaly'
          });
        });
        
        // Add GLDAS data converted to anomalies
        // Calculate 2018 baseline
        const gldas2018 = gldasData.filter(d => d.year === 2018);
        const baselineKg = gldas2018.reduce((sum, d) => sum + d.groundwater_cm, 0) / gldas2018.length;
        
        // Convert GLDAS to anomalies and rough cm equivalent
        // Rough conversion: 10 kg/m² ≈ 1 cm of water
        const graceEndValue = -8.727905291100553; // Exact last GRACE value in 2017
        
        gldasData.forEach(d => {
          const anomalyKg = d.groundwater_cm - baselineKg;
          const anomalyCmEquivalent = anomalyKg / 10; // Convert to cm scale
          
          combinedData.push({
            date: d.date,
            value: graceEndValue + anomalyCmEquivalent, // Apply GRACE offset for continuity
            source: 'GLDAS',
            type: 'estimated_anomaly'
          });
        });
        
        // Sort by date
        combinedData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        
        // Calculate statistics
        const graceTimelineValues = combinedData.filter(d => d.source === 'GRACE').map(d => d.value);
        const gldasTimelineValues = combinedData.filter(d => d.source === 'GLDAS').map(d => d.value);
        
        return jsonResponse({
          success: true,
          data: combinedData,
          summary: {
            grace_period: {
              start: '2002',
              end: '2017',
              final_value: graceTimelineValues[graceTimelineValues.length - 1] || null,
              trend: 'Declining at -0.81 cm/year'
            },
            gldas_period: {
              start: '2018',
              end: '2024',
              estimated_current: gldasTimelineValues[gldasTimelineValues.length - 1] || null,
              trend: 'Slight improvement (+0.15 cm/year equivalent)'
            },
            interpretation: 'GLDAS data suggests possible stabilization after severe depletion'
          }
        });

      case '/api/districts/groundwater':
        // Complete district data matching Flask API
        const regionalPatterns = {
          'Punjab': {
            'Lahore': -12.5,
            'Faisalabad': -10.8,
            'Multan': -9.2,
            'Rawalpindi': -6.5,
            'Gujranwala': -11.3,
            'Sialkot': -9.8,
            'Sargodha': -10.9,
            'Bahawalpur': -8.1,
            'Sheikhupura': -10.2,
            'Jhang': -7.4
          },
          'Sindh': {
            'Karachi': -4.3,
            'Hyderabad': -6.5,
            'Sukkur': -7.8,
            'Larkana': -8.4,
            'Mirpur Khas': -7.1,
            'Nawabshah': -8.0,
            'Jacobabad': -9.3,
            'Shikarpur': -8.9
          },
          'Khyber Pakhtunkhwa': {
            'Peshawar': -5.3,
            'Mardan': -4.8,
            'Mingora': -1.2,
            'Abbottabad': -2.1,
            'Mansehra': -2.8,
            'Kohat': -6.0,
            'Dera Ismail Khan': -7.1
          },
          'Balochistan': {
            'Quetta': -15.3,
            'Gwadar': -3.5,
            'Turbat': -6.1,
            'Khuzdar': -10.0,
            'Chaman': -13.0,
            'Zhob': -8.6,
            'Sibi': -11.4
          }
        };
        
        // Convert to features array
        const districtFeatures = [];
        for (const [province, districts] of Object.entries(regionalPatterns)) {
          for (const [district, change] of Object.entries(districts)) {
            districtFeatures.push({
              district,
              province,
              groundwater_change: change,
              status: change < -10 ? 'Critical' : change < -5 ? 'Warning' : change < 0 ? 'Moderate' : 'Improving'
            });
          }
        }
        
        // Calculate summary statistics
        const allValues = districtFeatures.map(d => d.groundwater_change);
        const avgChange = allValues.reduce((a, b) => a + b, 0) / allValues.length;
        
        return jsonResponse({
          success: true,
          data: {
            type: 'FeatureCollection',
            features: districtFeatures.map(d => ({
              type: 'Feature',
              properties: d,
              geometry: {
                type: 'Point',
                coordinates: []  // Empty as we handle coordinates in frontend
              }
            }))
          },
          summary: {
            total_districts: districtFeatures.length,
            average_change: avgChange,
            most_depleted: Math.min(...allValues),
            most_improved: Math.max(...allValues),
            critical_districts: allValues.filter(v => v < -10).length,
            improving_districts: allValues.filter(v => v > 0).length,
            data_shown: districtFeatures.length,
            most_affected: 'Quetta'
          }
        });

      case '/api/predict':
        if (request.method !== 'POST') {
          return jsonResponse({ error: 'Method not allowed' }, 405);
        }
        
        try {
          const body = await request.json() as { years?: number };
          const years = body.years || 5;
          
          // Simple prediction based on recent trend
          const recentTrend = -0.81; // cm/year from historical data
          const lastValue = graceData[graceData.length - 1].groundwater_cm;
          
          const predictions = [];
          for (let i = 1; i <= years; i++) {
            predictions.push({
              year: 2017 + i,
              predicted_groundwater_cm: lastValue + (recentTrend * i),
              confidence: 'medium',
              method: 'Linear extrapolation'
            });
          }
          
          return jsonResponse({
            predictions,
            parameters: {
              base_year: 2017,
              trend_rate: recentTrend,
              years_predicted: years
            }
          });
        } catch (error) {
          return jsonResponse({ error: 'Invalid request body' }, 400);
        }

      default:
        return jsonResponse({ error: 'Not found' }, 404);
    }
  },
};