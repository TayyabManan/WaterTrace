// Test the GLDAS calculations
const gldasData = [
  { groundwater_cm: 242.72560958228482, year: 2018 },
  { groundwater_cm: 241.75090598549488, year: 2018 },
  { groundwater_cm: 244.2691754126007, year: 2018 },
  { groundwater_cm: 245.56216485675554, year: 2018 },
  { groundwater_cm: 246.26446921231664, year: 2018 },
  { groundwater_cm: 245.02240581316974, year: 2018 },
  { groundwater_cm: 248.19827299441212, year: 2018 },
  { groundwater_cm: 254.96138110227582, year: 2018 },
  { groundwater_cm: 254.71285251761014, year: 2018 },
  { groundwater_cm: 248.94915861752435, year: 2018 },
  { groundwater_cm: 244.53662891056823, year: 2018 },
  { groundwater_cm: 242.1259745320422, year: 2018 }
];

// Calculate 2018 baseline
const gldas2018 = gldasData.filter(d => d.year === 2018);
const baselineKg = gldas2018.reduce((sum, d) => sum + d.groundwater_cm, 0) / gldas2018.length;

console.log('2018 Baseline:', baselineKg);

// Test conversion for first few points
const graceEndValue = -8.727905291100553;

console.log('\nFirst few GLDAS conversions:');
gldasData.slice(0, 5).forEach(d => {
  const anomalyKg = d.groundwater_cm - baselineKg;
  const anomalyCmEquivalent = anomalyKg / 10;
  const finalValue = graceEndValue + anomalyCmEquivalent;
  
  console.log(`Raw: ${d.groundwater_cm} → Anomaly: ${anomalyKg.toFixed(2)} → CM: ${anomalyCmEquivalent.toFixed(2)} → Final: ${finalValue.toFixed(2)}`);
});