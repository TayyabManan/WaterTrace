import React from 'react';
import WaterTraceDashboard from './components/WaterTraceDashboard';
import { Analytics } from "@vercel/analytics/react"
import './App.css';

function App() {
  return (
    <div className="App">
      <WaterTraceDashboard />
      <Analytics />
    </div>
  );
}

export default App;