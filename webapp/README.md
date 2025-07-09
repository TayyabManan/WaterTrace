# WaterTrace Dashboard - Deployment Guide

## Overview
WaterTrace is a comprehensive groundwater monitoring dashboard for Pakistan, analyzing 22 years of satellite data (2002-2024) to track water resource changes.

## Features
- 📊 Interactive time series visualization of groundwater anomalies
- 🗺️ District-level interactive map showing water stress levels
- 📈 GLDAS trend analysis with machine learning predictions
- 📱 Fully responsive design for all devices
- 🔄 Real-time data from Flask API backend

## Tech Stack
- **Frontend**: React 18, Recharts, Leaflet, Tailwind CSS
- **Backend**: Flask, Pandas, NumPy, Scikit-learn
- **Data Sources**: GRACE satellite data (2002-2017), GLDAS soil moisture (2018-2024)

## Local Development

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Backend Setup
```bash
cd webapp/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-cors pandas numpy joblib

# Run the backend
python app.py
```
Backend will run on http://localhost:5000

### Frontend Setup
```bash
cd webapp/frontend

# Install dependencies
npm install

# Start development server
npm start
```
Frontend will run on http://localhost:3000

## Production Deployment

### Backend Deployment (Heroku/Railway)

1. Create `requirements.txt` in backend folder:
```
flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
numpy==1.24.3
joblib==1.3.2
gunicorn==21.2.0
```

2. Create `Procfile`:
```
web: gunicorn app:app
```

3. Deploy to Heroku:
```bash
heroku create watertrace-api
heroku git:remote -a watertrace-api
git push heroku main
```

### Frontend Deployment (Vercel/Netlify)

1. Update API endpoint in frontend code:
```javascript
// Create .env.production
REACT_APP_API_URL=https://your-backend-url.herokuapp.com
```

2. Build for production:
```bash
npm run build
```

3. Deploy to Vercel:
```bash
npm i -g vercel
vercel --prod
```

Or deploy to Netlify:
- Drag and drop the `build` folder to Netlify
- Set up environment variables

### Environment Variables

Backend:
- `FLASK_ENV`: production
- `PORT`: (automatically set by platform)

Frontend:
- `REACT_APP_API_URL`: Your backend API URL

## Data Updates

To update the groundwater data:
1. Place new CSV files in `data/csv/`
2. Run the analysis scripts in `notebooks/`
3. Restart the backend server

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/analysis/summary` - Project summary
- `GET /api/historical/timeseries` - GRACE data (2002-2017)
- `GET /api/recent/timeseries` - GLDAS data (2018-2024)
- `GET /api/combined/timeline` - Combined timeline with proper scaling
- `GET /api/gldas/trend-analysis` - GLDAS trend analysis
- `GET /api/districts/groundwater` - District-level data for map

## Performance Optimizations

- Charts use ResponsiveContainer for mobile optimization
- Lazy loading for map components
- API responses are cached for 15 minutes
- Image assets optimized for web

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is part of Tayyab Manan's GIS Portfolio. All rights reserved.

## Contact

**Tayyab Manan**
- GitHub: [@tayyabmanan](https://github.com/tayyabmanan)
- Portfolio: [tayyabmanan.vercel.app](https://tayyabmanan.vercel.app/)

## Acknowledgments

- GRACE satellite mission (NASA/DLR)
- GLDAS data system (NASA/NOAA)
- Pakistan Survey Department for shapefiles