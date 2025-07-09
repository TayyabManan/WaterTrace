// webapp/frontend/src/components/WaterTraceDashboard.js
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import GroundwaterMap from './GroundwaterMap';
import './WaterTrace.css';
import API_URL from '../config';

const WaterTraceDashboard = () => {
  const [historicalData, setHistoricalData] = useState([]);
  const [recentData, setRecentData] = useState([]);
  const [combinedData, setCombinedData] = useState([]);
  const [gldasAnalysis, setGldasAnalysis] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      console.log('API URL:', API_URL);
      console.log('Fetching data from WaterTrace backend...');
      
      // Fetch all data
      const [historicalRes, recentRes, summaryRes, gldasRes, combinedRes] = await Promise.all([
        fetch(`${API_URL}/api/historical/timeseries`),
        fetch(`${API_URL}/api/recent/timeseries`), 
        fetch(`${API_URL}/api/analysis/summary`),
        fetch(`${API_URL}/api/gldas/trend-analysis`),
        fetch(`${API_URL}/api/combined/timeline`)
      ]);

      const historical = await historicalRes.json();
      const recent = await recentRes.json();
      const summaryData = await summaryRes.json();
      const gldasData = await gldasRes.json();
      const combinedTimeline = await combinedRes.json();

      setHistoricalData(historical.data || []);
      setRecentData(recent.data || []);
      
      // Use properly scaled combined data from backend
      setCombinedData(combinedTimeline.data || []);
      setSummary(summaryData);
      setGldasAnalysis(gldasData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading WaterTrace Dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8 text-center px-4">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-blue-900 mb-2">
            WaterTrace: Pakistan Groundwater Monitoring
          </h1>
          <p className="text-blue-700 text-sm sm:text-base md:text-lg mb-2">
            Comprehensive satellite-based groundwater analysis for Pakistan (2002-2024)
          </p>
          <p className="text-blue-600 text-xs sm:text-sm">
            Developed by <a href="https://github.com/tayyabmanan" target="_blank" rel="noopener noreferrer" className="font-semibold hover:text-blue-800 underline">Tayyab Manan</a>
          </p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-8">
            <Card className="bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader className="pb-1 sm:pb-2">
                <CardTitle className="text-xs sm:text-sm font-medium text-blue-600">Study Area</CardTitle>
              </CardHeader>
              <CardContent className="pt-1 sm:pt-2">
                <div className="text-xl sm:text-2xl font-bold text-blue-900">{summary.study_area.districts}</div>
                <p className="text-[10px] sm:text-xs text-blue-600">Districts</p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader className="pb-1 sm:pb-2">
                <CardTitle className="text-xs sm:text-sm font-medium text-blue-600">Historical</CardTitle>
              </CardHeader>
              <CardContent className="pt-1 sm:pt-2">
                <div className="text-xl sm:text-2xl font-bold text-blue-900">{summary.datasets.historical.data_points}</div>
                <p className="text-[10px] sm:text-xs text-blue-600">GRACE data</p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader className="pb-1 sm:pb-2">
                <CardTitle className="text-xs sm:text-sm font-medium text-blue-600">Recent</CardTitle>
              </CardHeader>
              <CardContent className="pt-1 sm:pt-2">
                <div className="text-xl sm:text-2xl font-bold text-blue-900">{summary.datasets.recent.data_points}</div>
                <p className="text-[10px] sm:text-xs text-blue-600">GLDAS data</p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader className="pb-1 sm:pb-2">
                <CardTitle className="text-xs sm:text-sm font-medium text-blue-600">Coverage</CardTitle>
              </CardHeader>
              <CardContent className="pt-1 sm:pt-2">
                <div className="text-xl sm:text-2xl font-bold text-blue-900">22</div>
                <p className="text-[10px] sm:text-xs text-blue-600">Years</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Analysis Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="w-full overflow-x-auto flex flex-nowrap md:grid md:grid-cols-6 gap-1 p-1">
            <TabsTrigger value="overview" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Overview</TabsTrigger>
            <TabsTrigger value="map" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Map</TabsTrigger>
            <TabsTrigger value="historical" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Historical</TabsTrigger>
            <TabsTrigger value="recent" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Recent</TabsTrigger>
            <TabsTrigger value="comparison" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Analysis</TabsTrigger>
            <TabsTrigger value="conclusion" className="whitespace-nowrap px-3 py-2 text-xs sm:text-sm">Conclusion</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
              <CardHeader>
                <CardTitle className="text-blue-900">Complete Timeline: Pakistan Groundwater Monitoring (2002-2024)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300} minHeight={250}>
                  <LineChart data={combinedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fill: '#1e40af' }}
                      stroke="#3b82f6"
                    />
                    <YAxis 
                      tick={{ fill: '#1e40af' }}
                      stroke="#3b82f6"
                    />
                    <Tooltip 
                      formatter={(value, name) => [value.toFixed(2), name]}
                      contentStyle={{ backgroundColor: '#eff6ff', border: '1px solid #3b82f6' }}
                    />
                    <Legend />
                    <ReferenceLine y={0} stroke="#666" strokeDasharray="5 5" label="Normal Level" />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#2563eb" 
                      strokeWidth={2}
                      name="Groundwater Anomaly (cm)"
                      dot={(props) => {
                        const { cx, cy, payload } = props;
                        return (
                          <circle 
                            cx={cx} 
                            cy={cy} 
                            r={2} 
                            fill={payload.source === 'GRACE' ? '#1d4ed8' : '#059669'}
                          />
                        );
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 border border-blue-300 rounded-lg">
                    <p className="font-semibold text-blue-900">📊 Data Sources</p>
                    <div className="text-sm text-blue-800 mt-2 space-y-1">
                      <p>• <strong>Blue dots (2002-2017):</strong> GRACE satellite measurements</p>
                      <p>• <strong>Green dots (2018-2024):</strong> GLDAS-derived estimates</p>
                      <p>• Values show deviation from normal groundwater levels</p>
                    </div>
                  </div>
                  <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg">
                    <p className="font-semibold text-amber-900">📈 Key Trends</p>
                    <div className="text-sm text-amber-800 mt-2 space-y-1">
                      <p>• <strong>2002-2017:</strong> Severe depletion (-0.81 cm/year)</p>
                      <p>• <strong>2018-2024:</strong> Possible stabilization (+0.15 cm/year)</p>
                      <p>• Current estimate: ~-7.6 cm below normal</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Interactive Map Tab */}
          <TabsContent value="map" className="space-y-6">
            <GroundwaterMap />
          </TabsContent>

          {/* Historical Tab */}
          <TabsContent value="historical" className="space-y-6">
            <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
              <CardHeader>
                <CardTitle className="text-blue-900">Historical Groundwater Trends (GRACE 2002-2017)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300} minHeight={250}>
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => [value, 'Groundwater Anomaly (cm)']} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="groundwater_cm" 
                      stroke="#2563eb" 
                      strokeWidth={2}
                      name="Groundwater (cm)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recent Tab */}
          <TabsContent value="recent" className="space-y-6">
            <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
              <CardHeader>
                <CardTitle className="text-blue-900">Recent Water Status Analysis (GLDAS 2018-2024)</CardTitle>
              </CardHeader>
              <CardContent>
                {gldasAnalysis && gldasAnalysis.success && (
                  <div className="space-y-6">
                    {/* Trend Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className={`p-4 rounded-lg ${gldasAnalysis.analysis.annual_change > 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                        <h4 className="font-semibold text-gray-900">Annual Trend</h4>
                        <p className={`text-2xl font-bold ${gldasAnalysis.analysis.annual_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {gldasAnalysis.analysis.annual_change > 0 ? '+' : ''}{gldasAnalysis.analysis.annual_change.toFixed(2)} kg/m²/year
                        </p>
                        <p className="text-sm text-gray-600">{gldasAnalysis.analysis.trend_direction}</p>
                      </div>
                      
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h4 className="font-semibold text-gray-900">Total Change</h4>
                        <p className="text-2xl font-bold text-blue-600">
                          {gldasAnalysis.analysis.total_change > 0 ? '+' : ''}{gldasAnalysis.analysis.total_change.toFixed(1)} kg/m²
                        </p>
                        <p className="text-sm text-gray-600">Since 2018</p>
                      </div>
                      
                      <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                        <h4 className="font-semibold text-gray-900">Interpretation</h4>
                        <p className="text-sm font-medium text-amber-800">
                          {gldasAnalysis.analysis.interpretation}
                        </p>
                      </div>
                    </div>

                    {/* Anomaly Chart */}
                    <div>
                      <h4 className="text-lg font-semibold text-blue-900 mb-3">Soil Moisture Anomalies from 2018 Baseline</h4>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={gldasAnalysis.time_series}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                          <XAxis dataKey="date" tick={{ fill: '#1e40af' }} />
                          <YAxis tick={{ fill: '#1e40af' }} />
                          <Tooltip formatter={(value) => [`${value.toFixed(2)} kg/m²`, 'Anomaly']} />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="anomaly" 
                            stroke="#2563eb" 
                            strokeWidth={2}
                            name="Change from 2018 baseline"
                            dot={{ r: 2 }}
                          />
                          <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Absolute Values Chart */}
                    <div className="mt-6">
                      <h4 className="text-lg font-semibold text-blue-900 mb-3">Absolute Soil Moisture Values</h4>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={recentData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                          <XAxis dataKey="date" tick={{ fill: '#1e40af' }} />
                          <YAxis tick={{ fill: '#1e40af' }} />
                          <Tooltip formatter={(value) => [`${value.toFixed(2)} kg/m²`, 'Soil Moisture']} />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="groundwater_cm" 
                            stroke="#059669" 
                            strokeWidth={2}
                            name="Deep Soil Moisture (100-200cm)"
                            dot={{ r: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Important Note */}
                    <div className="mt-6 p-4 bg-blue-50 border border-blue-300 rounded-lg">
                      <h4 className="font-semibold text-blue-900 mb-2">Understanding GLDAS Data</h4>
                      <ul className="space-y-2 text-sm text-blue-800">
                        <li>• GLDAS measures deep soil moisture (100-200cm depth) as a proxy for groundwater</li>
                        <li>• The {gldasAnalysis.analysis.annual_change > 0 ? 'increasing' : 'decreasing'} trend of {Math.abs(gldasAnalysis.analysis.annual_change).toFixed(2)} kg/m²/year suggests {gldasAnalysis.analysis.annual_change > 0 ? 'improving water retention' : 'continued water stress'}</li>
                        <li>• {gldasAnalysis.analysis.comparison_note}</li>
                        <li>• For definitive groundwater assessment, GRACE-FO satellite data integration is needed</li>
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Comparison Tab */}
          <TabsContent value="comparison" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-blue-900">Dataset Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-semibold">GRACE (2002-2017)</h4>
                      <p className="text-sm text-gray-600">Direct groundwater measurements</p>
                      <p className="text-sm text-gray-600">163 data points over 15 years</p>
                    </div>
                    <div className="border-l-4 border-green-500 pl-4">
                      <h4 className="font-semibold">GLDAS (2018-2024)</h4>
                      <p className="text-sm text-gray-600">Soil moisture proxy for groundwater</p>
                      <p className="text-sm text-gray-600">Monthly averages from 3-hourly data</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-blue-900">Key Findings</CardTitle>
                </CardHeader>
                <CardContent>
                  {summary && (
                    <ul className="space-y-2">
                      {summary.key_findings.map((finding, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-500 mr-2">✓</span>
                          <span className="text-sm">{finding}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Conclusion Tab */}
          <TabsContent value="conclusion" className="space-y-6">
            <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
              <CardHeader>
                <CardTitle className="text-blue-900 text-2xl">Research Conclusion: 22 Years of Groundwater Monitoring</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="prose max-w-none text-blue-800">
                  <h3 className="text-xl font-semibold text-blue-900 mb-4">Critical Water Crisis in Pakistan (2002-2024)</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                      <h4 className="font-semibold text-red-900 mb-2">Historical Period (2002-2017)</h4>
                      <ul className="space-y-2 text-red-800">
                        <li>• <strong>Severe Depletion:</strong> -13.71 cm total groundwater loss</li>
                        <li>• <strong>Annual Decline:</strong> -0.81 cm/year consistent depletion</li>
                        <li>• <strong>Average State:</strong> -1.85 cm below normal levels</li>
                        <li>• <strong>Statistical Significance:</strong> p-value &lt; 0.001 (highly significant)</li>
                      </ul>
                    </div>
                    
                    <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded">
                      <h4 className="font-semibold text-amber-900 mb-2">Recent Period (2018-2024)</h4>
                      <ul className="space-y-2 text-amber-800">
                        <li>• <strong>Data Source:</strong> GLDAS soil moisture (proxy indicator)</li>
                        <li>• <strong>Trend:</strong> +1.5 kg/m²/year slight increase</li>
                        <li>• <strong>Interpretation:</strong> Possible stabilization or modest improvement</li>
                        <li>• <strong>Caution:</strong> Needs GRACE-FO validation for confirmation</li>
                      </ul>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-300 rounded-lg p-6 mb-6">
                    <h4 className="text-lg font-semibold text-blue-900 mb-3">Key Findings & Implications</h4>
                    <div className="space-y-3 text-blue-800">
                      <p><strong>1. Long-term Water Stress:</strong> Pakistan experienced severe groundwater depletion for 15+ years, likely due to:</p>
                      <ul className="ml-6 list-disc">
                        <li>Excessive groundwater pumping for agriculture</li>
                        <li>Rapid urbanization and increased water demand</li>
                        <li>Climate change impacts on precipitation patterns</li>
                        <li>Inefficient irrigation practices</li>
                      </ul>
                      
                      <p><strong>2. Recent Trends (2018-2024):</strong> GLDAS analysis suggests:</p>
                      <ul className="ml-6 list-disc">
                        <li>Slight increase in deep soil moisture (+1.5 kg/m²/year)</li>
                        <li>Possible stabilization after years of depletion</li>
                        <li>May indicate improved water management or better rainfall</li>
                        <li>However, GRACE-FO data needed for definitive assessment</li>
                      </ul>
                      
                      <p><strong>3. Seasonal Variations:</strong> Data shows significant seasonal patterns:</p>
                      <ul className="ml-6 list-disc">
                        <li>Lowest levels: January, May, November (dry months)</li>
                        <li>Highest levels: July-August (monsoon season)</li>
                        <li>Critical stress periods require targeted management</li>
                      </ul>
                    </div>
                  </div>

                  <div className="bg-amber-50 border border-amber-300 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-amber-900 mb-3">Recommendations for Sustainable Water Future</h4>
                    <ol className="space-y-2 text-amber-800 list-decimal ml-6">
                      <li><strong>Continue Monitoring:</strong> Maintain satellite-based surveillance to track progress</li>
                      <li><strong>Policy Enforcement:</strong> Strengthen groundwater extraction regulations</li>
                      <li><strong>Agricultural Reform:</strong> Promote drip irrigation and water-efficient crops</li>
                      <li><strong>Rainwater Harvesting:</strong> Implement large-scale collection systems</li>
                      <li><strong>Public Awareness:</strong> Educate communities about water conservation</li>
                      <li><strong>Regional Planning:</strong> Develop district-specific water management strategies</li>
                    </ol>
                  </div>

                  <div className="mt-6 p-4 bg-gradient-to-r from-amber-100 to-blue-100 rounded-lg text-center">
                    <p className="text-blue-900 font-medium">
                      "Pakistan faced severe groundwater depletion (-0.81 cm/year) from 2002-2017. GLDAS data (2018-2024) 
                      shows a slight increase in soil moisture (+1.5 kg/m²/year), suggesting possible stabilization. 
                      However, this cautiously optimistic trend requires validation with GRACE-FO satellite data for confirmation."
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-blue-200">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Tayyab Manan</h3>
            <p className="text-blue-700 mb-4">GIS Developer & Spatial Analyst</p>
            <div className="flex justify-center space-x-6">
              <a 
                href="https://github.com/TayyabManan" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
              <a 
                href="https://tayyabmanan.vercel.app/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </a>
            </div>
            <p className="text-sm text-blue-600 mt-4">
              © 2025 WaterTrace - Monitoring Pakistan's Water Resources
            </p>
          </div>
        </footer>

      </div>
    </div>
  );
};

export default WaterTraceDashboard;