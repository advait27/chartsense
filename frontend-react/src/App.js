import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import AnalysisResults from './components/AnalysisResults';
import LoadingAnimation from './components/LoadingAnimation';
import ErrorMessage from './components/ErrorMessage';
import ChatInterface from './components/ChatInterface';
import axios from 'axios';

// Configuration from environment variables
const API_URL = process.env.REACT_APP_API_URL || '/api';
const ENABLE_CHAT = process.env.REACT_APP_ENABLE_CHAT !== 'false';
const APP_VERSION = process.env.REACT_APP_VERSION || '1.0.0';

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
      // Use environment-based API URL
      const apiEndpoint = `${API_URL}/analyze`;
      console.log('Calling API:', apiEndpoint);
      
      const response = await axios.post(apiEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for Llama reasoning model
      });

      setAnalysisData(response.data);
      setError(null);
    } catch (err) {
      console.error('Analysis error:', err);
      
      let errorMessage = 'Failed to analyze chart. Please try again.';
      
      if (err.response) {
        // Server responded with error
        errorMessage = err.response.data?.message || err.response.data?.error || errorMessage;
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something else went wrong
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
      
      // Only use mock data in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Using mock data for development');
        setAnalysisData(getMockAnalysisData());
        setError(null);
      }
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
      },
      trading_signals: {
        signal_type: "SELL",
        entry_level: "1.1750-1.1780 (on pullback)",
        stop_loss: "1.1850 (70 pips)",
        take_profit_1: "1.1610 (140 pips)",
        take_profit_2: "1.1550 (200 pips)",
        risk_reward_ratio: "1:2 (TP1) or 1:2.8 (TP2)",
        position_sizing: "Risk 1-2% of capital per trade. Recommended 1.5% for this setup.",
        timeframe_context: "Best suited for 4H-Daily swing trades",
        confidence_score: "High (75-80%)"
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
              
              {ENABLE_CHAT && <ChatInterface analysisData={analysisData} />}
            </>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>Powered by AI • {analysisData?.metadata?.vision_model || 'Qwen Vision'} & {analysisData?.metadata?.reasoning_model || 'Llama Reasoning'}</p>
        <p className="disclaimer">⚠️ Educational purposes only. Not financial advice.</p>
        <p className="version">v{APP_VERSION}</p>
      </footer>
    </div>
  );
}

export default App;
