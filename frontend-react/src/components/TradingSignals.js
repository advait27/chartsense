import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Shield, 
  DollarSign,
  Clock,
  AlertTriangle,
  BarChart3
} from 'lucide-react';
import './TradingSignals.css';

const TradingSignals = ({ signals }) => {
  if (!signals) return null;

  const getSignalBadgeClass = (signalType) => {
    const type = signalType?.toLowerCase() || '';
    if (type.includes('buy')) return 'signal-badge buy';
    if (type.includes('sell')) return 'signal-badge sell';
    if (type.includes('wait')) return 'signal-badge wait';
    return 'signal-badge no-signal';
  };

  const getSignalIcon = (signalType) => {
    const type = signalType?.toLowerCase() || '';
    if (type.includes('buy')) return <TrendingUp size={24} />;
    if (type.includes('sell')) return <TrendingDown size={24} />;
    return <BarChart3 size={24} />;
  };

  const getConfidencePercentage = (confidence) => {
    if (!confidence) return 50;
    const conf = confidence.toLowerCase();
    if (conf.includes('high')) return 80;
    if (conf.includes('medium')) return 60;
    if (conf.includes('low')) return 40;
    
    // Try to extract percentage
    const match = confidence.match(/(\d+)/);
    if (match) return parseInt(match[1]);
    
    return 50;
  };

  return (
    <div className="trading-signals">
      <div className="signal-header">
        <div className="signal-title">
          {getSignalIcon(signals.signal_type)}
          <span>Trading Signals</span>
        </div>
        <div className={getSignalBadgeClass(signals.signal_type)}>
          {signals.signal_type || 'WAIT'}
        </div>
      </div>

      <div className="signal-grid">
        {signals.entry_level && signals.entry_level !== 'Not specified' && (
          <div className="signal-card">
            <div className="signal-card-label">
              <Target size={16} />
              Entry Level
            </div>
            <div className="signal-card-value highlight">
              {signals.entry_level}
            </div>
          </div>
        )}

        {signals.stop_loss && signals.stop_loss !== 'Not specified' && (
          <div className="signal-card">
            <div className="signal-card-label">
              <Shield size={16} />
              Stop Loss
            </div>
            <div className="signal-card-value">
              {signals.stop_loss}
            </div>
          </div>
        )}

        {signals.take_profit_1 && signals.take_profit_1 !== 'Not specified' && (
          <div className="signal-card">
            <div className="signal-card-label">
              <Target size={16} />
              Take Profit 1
            </div>
            <div className="signal-card-value">
              {signals.take_profit_1}
            </div>
          </div>
        )}

        {signals.take_profit_2 && (
          <div className="signal-card">
            <div className="signal-card-label">
              <Target size={16} />
              Take Profit 2
            </div>
            <div className="signal-card-value">
              {signals.take_profit_2}
            </div>
          </div>
        )}

        {signals.risk_reward_ratio && signals.risk_reward_ratio !== 'Not specified' && (
          <div className="signal-card">
            <div className="signal-card-label">
              <BarChart3 size={16} />
              Risk:Reward
            </div>
            <div className="signal-card-value highlight">
              {signals.risk_reward_ratio}
            </div>
          </div>
        )}

        {signals.timeframe_context && (
          <div className="signal-card">
            <div className="signal-card-label">
              <Clock size={16} />
              Timeframe
            </div>
            <div className="signal-card-value">
              {signals.timeframe_context}
            </div>
          </div>
        )}
      </div>

      <div className="signal-details">
        {signals.position_sizing && (
          <>
            <h4>
              <DollarSign size={16} style={{ display: 'inline', marginRight: '8px' }} />
              Position Sizing
            </h4>
            <p>{signals.position_sizing}</p>
          </>
        )}

        {signals.confidence_score && signals.confidence_score !== 'Not available' && (
          <div className="confidence-meter">
            <div className="confidence-label">
              <span>Confidence Score</span>
              <span>{signals.confidence_score}</span>
            </div>
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${getConfidencePercentage(signals.confidence_score)}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="disclaimer">
        <AlertTriangle size={14} className="disclaimer-icon" />
        <strong>Educational Purposes Only:</strong> These signals are for learning and analysis. 
        Not financial advice. Always do your own research and risk management.
      </div>
    </div>
  );
};

export default TradingSignals;
