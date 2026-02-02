# ChartSense React Frontend

Modern, dynamic React frontend for AI-powered chart analysis with a professional trading dark theme.

## Features

- 🎨 **Dark Trading Theme** - Professional color scheme optimized for trading applications
- 📊 **Drag & Drop Upload** - Easy chart image upload with preview
- 🤖 **Real-time Analysis** - Live AI-powered technical analysis
- ⚡ **Dynamic Animations** - Smooth transitions and loading states
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile
- 🎯 **Collapsible Sections** - Clean, organized results display
- 🔒 **Type-safe** - Built with modern React practices

## Tech Stack

- React 18
- Axios for API calls
- Framer Motion for animations
- Lucide React for icons
- React Dropzone for file uploads

## Installation

```bash
cd frontend-react
npm install
```

## Development

Start the development server:

```bash
npm start
```

The app will open at http://localhost:3000

## Building for Production

```bash
npm run build
```

## Backend Integration

Currently configured to work with a FastAPI backend on `http://localhost:8000`.

To integrate with the existing Python backend:
1. Convert the Streamlit backend to FastAPI
2. Add a `/api/analyze` endpoint that accepts multipart form data
3. Return JSON in the format expected by the frontend (see `App.js` for structure)

## Mock Data

The frontend includes mock data for demo purposes when the backend is unavailable. Check `App.js` `getMockAnalysisData()` function.

## Color Scheme

- Primary Background: `#0a0e1a`
- Secondary Background: `#131720`
- Accent Green (Bullish): `#10b981`
- Accent Red (Bearish): `#ef4444`
- Accent Blue: `#3b82f6`
- Accent Purple: `#8b5cf6`

## Components

- `Header` - Navigation bar with logo and status
- `UploadSection` - Drag & drop file upload area
- `LoadingAnimation` - Analysis in progress state
- `AnalysisResults` - Display comprehensive analysis results
- `ErrorMessage` - Error handling and display

## License

MIT
