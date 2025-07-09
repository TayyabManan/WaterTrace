import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Legend } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import API_URL from '../config';

// Pakistan district coordinates (major cities)
const districtCoordinates = {
  // Punjab
  'Lahore': [31.5497, 74.3436],
  'Faisalabad': [31.4504, 73.1350],
  'Multan': [30.1968, 71.4784],
  'Rawalpindi': [33.5977, 73.0479],
  'Gujranwala': [32.1616, 74.1883],
  'Sialkot': [32.4927, 74.5319],
  'Sargodha': [32.0854, 72.6690],
  'Bahawalpur': [29.3956, 71.6836],
  'Sheikhupura': [31.7167, 73.9850],
  'Jhang': [31.2781, 72.3317],
  
  // Sindh
  'Karachi': [24.8607, 67.0011],
  'Hyderabad': [25.3924, 68.3737],
  'Sukkur': [27.7017, 68.8570],
  'Larkana': [27.5580, 68.2141],
  'Mirpur Khas': [25.5276, 69.0111],
  'Nawabshah': [26.2483, 68.4096],
  'Jacobabad': [28.2769, 68.4514],
  'Shikarpur': [27.9556, 68.6382],
  
  // Khyber Pakhtunkhwa
  'Peshawar': [34.0151, 71.5249],
  'Mardan': [34.1986, 72.0404],
  'Mingora': [34.7717, 72.3602],
  'Abbottabad': [34.1495, 73.1995],
  'Mansehra': [34.3302, 73.1968],
  'Kohat': [33.5869, 71.4414],
  'Dera Ismail Khan': [31.8313, 70.9017],
  
  // Balochistan
  'Quetta': [30.1798, 66.9750],
  'Gwadar': [25.1266, 62.3225],
  'Turbat': [26.0031, 63.0518],
  'Khuzdar': [27.8000, 66.6167],
  'Chaman': [30.9236, 66.4512],
  'Zhob': [31.3417, 69.4493],
  'Sibi': [29.5430, 67.8773]
};

const GroundwaterMap = () => {
  const [districtData, setDistrictData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDistrictData();
  }, []);

  const fetchDistrictData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/districts/groundwater`);
      const data = await response.json();
      setDistrictData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching district data:', error);
      setLoading(false);
    }
  };

  const getMarkerColor = (change) => {
    if (change < -10) return '#dc2626'; // red - critical
    if (change < -5) return '#f59e0b'; // orange - warning
    if (change < 0) return '#eab308'; // yellow - moderate
    return '#22c55e'; // green - improving
  };

  const getMarkerSize = (change) => {
    const absChange = Math.abs(change);
    if (absChange > 15) return 25;
    if (absChange > 10) return 20;
    if (absChange > 5) return 15;
    return 10;
  };

  if (loading || !districtData) {
    return <div className="flex justify-center items-center h-96">Loading map data...</div>;
  }

  // Custom control component for the legend
  const MapLegend = () => (
    <div className="leaflet-bottom leaflet-right">
      <div className="leaflet-control leaflet-bar bg-white p-4 rounded shadow-lg">
        <h4 className="text-sm font-semibold mb-2">Groundwater Change (cm)</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-600"></div>
            <span className="text-xs">Critical (&lt; -10)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500"></div>
            <span className="text-xs">Warning (-10 to -5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span className="text-xs">Moderate (-5 to 0)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-xs">Improving (&gt; 0)</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <Card className="bg-white/90 backdrop-blur-sm border-blue-200 shadow-xl">
        <CardHeader>
          <CardTitle className="text-blue-900">Interactive Groundwater Map - District Level Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="map-container" style={{ height: '500px', width: '100%' }}>
            <MapContainer
              center={[30.3753, 69.3451]} // Pakistan center
              zoom={5}
              style={{ height: '100%', width: '100%' }}
              className="rounded-lg"
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              
              {districtData.data.features.map((feature, index) => {
                const coords = districtCoordinates[feature.properties.district];
                if (!coords) return null;
                
                return (
                  <CircleMarker
                    key={index}
                    center={coords}
                    radius={getMarkerSize(feature.properties.groundwater_change)}
                    fillColor={getMarkerColor(feature.properties.groundwater_change)}
                    color="#1e3a8a"
                    weight={2}
                    opacity={0.8}
                    fillOpacity={0.7}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-bold text-lg">{feature.properties.district}</h3>
                        <p className="text-sm text-gray-600">{feature.properties.province}</p>
                        <div className="mt-2">
                          <p className="font-semibold">
                            Groundwater Change: 
                            <span className={`ml-2 ${feature.properties.groundwater_change < 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {feature.properties.groundwater_change.toFixed(1)} cm
                            </span>
                          </p>
                          <p className="text-sm mt-1">
                            Status: <span className={`font-semibold ${
                              feature.properties.status === 'Critical' ? 'text-red-600' :
                              feature.properties.status === 'Warning' ? 'text-amber-600' :
                              feature.properties.status === 'Moderate' ? 'text-yellow-600' :
                              'text-green-600'
                            }`}>{feature.properties.status}</span>
                          </p>
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
              
              <MapLegend />
            </MapContainer>
          </div>
          
          {/* Summary Statistics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-4 sm:mt-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-900">Critical Districts</h4>
              <p className="text-2xl font-bold text-red-600">{districtData.summary.critical_districts}</p>
              <p className="text-sm text-red-700">Depletion &gt; 10 cm</p>
            </div>
            
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h4 className="font-semibold text-amber-900">Average Change</h4>
              <p className="text-2xl font-bold text-amber-600">{districtData.summary.average_change.toFixed(1)} cm</p>
              <p className="text-sm text-amber-700">Across all districts</p>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900">Improving Districts</h4>
              <p className="text-2xl font-bold text-green-600">{districtData.summary.improving_districts}</p>
              <p className="text-sm text-green-700">Positive trend</p>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> This map shows representative groundwater changes based on regional patterns. 
              Larger circles indicate greater absolute change. Click on any marker for detailed information.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GroundwaterMap;