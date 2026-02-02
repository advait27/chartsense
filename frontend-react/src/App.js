import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import AnalysisResults from './components/AnalysisResults';
import LoadingAnimation from './components/LoadingAnimation';
import ErrorMessage from './components/ErrorMessage';
import ChatInterface from './components/ChatInterface';
import axios from 'axios';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setAnalysisData(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => setUploadedImage(e.target.result);
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('chart', file);

    try {
      // Since backend is Streamlit, we'll simulate the API call
      // In production, you'd need to convert backend to FastAPI
      const response = await axios.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 90000, // 90 seconds
      });

      setAnalysisData(response.data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(
        err.response?.data?.message || 
        err.message || 
        'Failed to analyze chart. Please try again.'
      );
      
      // For demo purposes, set mock data
      setAnalysisData(getMockAnalysisData());
    } finally {
      setLoading(false);
    }
  };

  const getMockAnalysisData = () => ({
    vision: {
      chart_type: "Candlestick Chart",
      timeframe: "4H",
      price_structure: "The chart displays a bearish trend with lower highs and lower lows. Price has declined from 1.20 to 1.16 area.",
      indicators_detected: ["MA 20", "MA 50", "Volume"],
      visual_patterns: ["Descending Channel", "Double Top"],
      momentum_signals: "Volume increasing on down moves suggests bearish pressure."
    },
    reasoning: {
      market_structure: {
        trend_description: "The current market structure suggests a bearish trend, characterized by a descending channel and potential double top pattern. Key support identified around 1.16-1.17 area, with resistance near 1.19-1.20.",
        key_levels: ["Support: 1.16", "Support: 1.17", "Resistance: 1.19", "Resistance: 1.20"],
        structural_notes: []
      },
      momentum: {
        assessment: "Momentum indicators show continued bearish pressure. Volume analysis suggests increased selling on down moves, confirming the trend direction.",
        indicators: ["Volume confirmation"],
        divergences: [],
        strength: "Strong Bearish"
      },
      regime: {
        regime: "Trending Bearish",
        reasoning: "Clear downtrend with descending channel formation and lower swing points. Market showing directional conviction.",
        volatility: "Moderate"
      },
      strategy_bias: {
        bias: "Bearish",
        confidence: "High",
        reasoning: [
          "Descending channel pattern intact",
          "Consistent lower highs and lower lows",
          "Volume confirming bearish moves",
          "Price below key moving averages"
        ]
      },
      suitable_approaches: {
        approaches: [
          { name: "Trend Following", rationale: "Trade with the established downtrend" },
          { name: "Breakout Trading", rationale: "Wait for break below support for continuation" }
        ]
      },
      invalidation: {
        bullish_invalidation: ["Break and hold above 1.20 resistance"],
        bearish_invalidation: ["Price fails to make new lows and breaks above 1.19"],
        key_levels: ["1.16 (critical support)", "1.20 (critical resistance)"]
      }
    },
    metadata: {
      timestamp: new Date().toISOString(),
      vision_model: "Qwen/Qwen2.5-VL-7B-Instruct",
      reasoning_model: "meta-llama/Llama-3.3-70B-Instruct"
    }
  });

  return (
    <div className="App">
      <Header />
      
      <main className="main-content">
        <div className="container">
          <UploadSection 
            onFileUpload={handleFileUpload}
            loading={loading}
          />

          {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
          
          {loading && <LoadingAnimation />}
          
          {analysisData && !loading && (
            <>
              <AnalysisResults 
                data={analysisData} 
                imagePreview={uploadedImage}
              />
              
              <ChatInterface analysisData={analysisData} />
            </>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>Powered by AI • {analysisData?.metadata?.vision_model || 'Qwen Vision'} & {analysisData?.metadata?.reasoning_model || 'Llama Reasoning'}</p>
        <p className="disclaimer">⚠️ Educational purposes only. Not financial advice.</p>
      </footer>
    </div>
  );
}

export default App;
