import React, { useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  AlertTriangle, 
  ChevronDown,
  ChevronUp,
  Image as ImageIcon,
  Zap,
  Eye
} from 'lucide-react';
import './AnalysisResults.css';

// Helper function to render markdown-style text
const renderFormattedText = (text) => {
  if (!text) return null;
  
  // Replace **text** with <strong>text</strong>
  const parts = text.split(/(\*\*.*?\*\*)/g);
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
};

// Parse and structure price structure text
const parsePriceStructure = (text) => {
  if (!text) return [];
  
  // Split by ' - **' to get sections
  const sections = text.split(/\s*-\s*\*\*/)
    .filter(s => s.trim())
    .map(s => s.replace(/\*\*/g, '').trim());
  
  return sections;
};

const AnalysisResults = ({ data, imagePreview }) => {
  const [expandedSections, setExpandedSections] = useState({
    vision: true,
    structure: true,
    momentum: true,
    regime: true,
    bias: true,
    approaches: true,
    invalidation: true,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getBiasColor = (bias) => {
    if (bias?.toLowerCase().includes('bullish')) return 'var(--accent-green)';
    if (bias?.toLowerCase().includes('bearish')) return 'var(--accent-red)';
    return 'var(--text-secondary)';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence?.toLowerCase() === 'high') return 'var(--accent-green)';
    if (confidence?.toLowerCase() === 'low') return 'var(--accent-red)';
    return 'var(--accent-yellow)';
  };

  return (
    <div className="results-container slide-up">
      <div className="results-header">
        <h2 className="results-title">📊 Analysis Results</h2>
        <div className="results-meta">
          <span className="meta-badge">
            <Eye size={14} />
            {data?.metadata?.vision_model?.split('/').pop() || 'Qwen Vision'}
          </span>
          <span className="meta-badge">
            <Zap size={14} />
            {data?.metadata?.reasoning_model?.split('/').pop() || 'Llama'}
          </span>
        </div>
      </div>

      {/* Chart Preview */}
      {imagePreview && (
        <div className="chart-section">
          <div className="section-header">
            <ImageIcon size={20} className="section-icon" />
            <h3>Your Chart</h3>
          </div>
          <div className="chart-image-container">
            <img src={imagePreview} alt="Analyzed chart" className="analyzed-chart" />
          </div>
        </div>
      )}

      {/* Vision Analysis */}
      <CollapsibleSection
        title="Vision Analysis"
        icon={<Eye size={20} />}
        expanded={expandedSections.vision}
        onToggle={() => toggleSection('vision')}
        badge="AI Vision"
      >
        <div className="info-grid">
          <InfoCard 
            label="Chart Type" 
            value={data?.vision?.chart_type || 'Unknown'} 
          />
          <InfoCard 
            label="Timeframe" 
            value={data?.vision?.timeframe && data.vision.timeframe !== 'Not specified' ? data.vision.timeframe : 'N/A'} 
          />
        </div>
        
        {data?.vision?.price_structure && (
          <div className="price-structure-section">
            <strong className="section-title">Price Structure</strong>
            <div className="structure-list">
              {parsePriceStructure(data.vision.price_structure).map((section, i) => {
                const [title, ...content] = section.split(':');
                return (
                  <div key={i} className="structure-item">
                    <strong className="structure-label">{title}:</strong>
                    <span className="structure-content">{content.join(':').trim()}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {data?.vision?.indicators_detected?.length > 0 && (
          <div className="indicators-section">
            <strong>Indicators Detected:</strong>
            <div className="tag-list">
              {data.vision.indicators_detected.map((indicator, i) => (
                <span key={i} className="tag">{renderFormattedText(indicator)}</span>
              ))}
            </div>
          </div>
        )}

        {data?.vision?.visual_patterns?.length > 0 && (
          <div className="patterns-section">
            <strong>Visual Patterns:</strong>
            <div className="tag-list">
              {data.vision.visual_patterns.map((pattern, i) => (
                <span key={i} className="tag pattern-tag">{renderFormattedText(pattern)}</span>
              ))}
            </div>
          </div>
        )}
      </CollapsibleSection>

      {/* Market Structure */}
      <CollapsibleSection
        title="Market Structure"
        icon={<TrendingUp size={20} />}
        expanded={expandedSections.structure}
        onToggle={() => toggleSection('structure')}
        badge="Technical"
      >
        <div className="analysis-text">
          <p>{data?.reasoning?.market_structure?.trend_description}</p>
        </div>

        {data?.reasoning?.market_structure?.key_levels?.length > 0 && (
          <div className="levels-grid">
            {data.reasoning.market_structure.key_levels.map((level, i) => (
              <div key={i} className="level-chip">
                <Target size={14} />
                {level}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      {/* Momentum */}
      <CollapsibleSection
        title="Momentum Analysis"
        icon={<Activity size={20} />}
        expanded={expandedSections.momentum}
        onToggle={() => toggleSection('momentum')}
        badge={data?.reasoning?.momentum?.strength}
        badgeColor={
          data?.reasoning?.momentum?.strength?.toLowerCase().includes('bearish') 
            ? 'var(--accent-red)' 
            : data?.reasoning?.momentum?.strength?.toLowerCase().includes('bullish')
            ? 'var(--accent-green)'
            : 'var(--accent-yellow)'
        }
      >
        <div className="analysis-text">
          <p>{data?.reasoning?.momentum?.assessment}</p>
        </div>
      </CollapsibleSection>

      {/* Market Regime */}
      <CollapsibleSection
        title="Market Regime"
        icon={<Activity size={20} />}
        expanded={expandedSections.regime}
        onToggle={() => toggleSection('regime')}
        badge={data?.reasoning?.regime?.regime}
        badgeColor={
          data?.reasoning?.regime?.regime?.toLowerCase().includes('bearish')
            ? 'var(--accent-red)'
            : data?.reasoning?.regime?.regime?.toLowerCase().includes('bullish')
            ? 'var(--accent-green)'
            : 'var(--text-secondary)'
        }
      >
        <div className="regime-info">
          <div className="regime-row">
            <span className="regime-label">Classification:</span>
            <span className="regime-value">{data?.reasoning?.regime?.regime}</span>
          </div>
          <div className="regime-row">
            <span className="regime-label">Volatility:</span>
            <span className="regime-value">{data?.reasoning?.regime?.volatility}</span>
          </div>
        </div>
        <div className="analysis-text">
          <p>{data?.reasoning?.regime?.reasoning}</p>
        </div>
      </CollapsibleSection>

      {/* Strategy Bias */}
      <CollapsibleSection
        title="Strategy Bias"
        icon={data?.reasoning?.strategy_bias?.bias?.toLowerCase().includes('bearish') 
          ? <TrendingDown size={20} /> 
          : <TrendingUp size={20} />}
        expanded={expandedSections.bias}
        onToggle={() => toggleSection('bias')}
        badge={data?.reasoning?.strategy_bias?.bias}
        badgeColor={getBiasColor(data?.reasoning?.strategy_bias?.bias)}
      >
        <div className="bias-header">
          <div className="bias-main">
            <span 
              className="bias-value" 
              style={{ color: getBiasColor(data?.reasoning?.strategy_bias?.bias) }}
            >
              {data?.reasoning?.strategy_bias?.bias}
            </span>
            <span 
              className="confidence-badge"
              style={{ 
                background: `${getConfidenceColor(data?.reasoning?.strategy_bias?.confidence)}20`,
                color: getConfidenceColor(data?.reasoning?.strategy_bias?.confidence)
              }}
            >
              {data?.reasoning?.strategy_bias?.confidence} Confidence
            </span>
          </div>
        </div>

        {data?.reasoning?.strategy_bias?.reasoning?.length > 0 && (
          <div className="reasoning-list">
            <strong>Supporting Evidence:</strong>
            <ul>
              {data.reasoning.strategy_bias.reasoning.map((reason, i) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </CollapsibleSection>

      {/* Suitable Approaches */}
      {data?.reasoning?.suitable_approaches?.approaches?.length > 0 && (
        <CollapsibleSection
          title="Suitable Approaches"
          icon={<Target size={20} />}
          expanded={expandedSections.approaches}
          onToggle={() => toggleSection('approaches')}
          badge="Strategies"
        >
          <div className="approaches-grid">
            {data.reasoning.suitable_approaches.approaches.map((approach, i) => (
              <div key={i} className="approach-card">
                <div className="approach-header">
                  <span className="approach-name">{approach.name}</span>
                </div>
                <p className="approach-rationale">{approach.rationale}</p>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Invalidation Conditions */}
      <CollapsibleSection
        title="Invalidation Conditions"
        icon={<AlertTriangle size={20} />}
        expanded={expandedSections.invalidation}
        onToggle={() => toggleSection('invalidation')}
        badge="Risk Management"
      >
        <div className="invalidation-grid">
          <div className="invalidation-card bullish">
            <div className="invalidation-header">
              <TrendingUp size={18} />
              <strong>Bullish Scenario</strong>
            </div>
            <ul>
              {data?.reasoning?.invalidation?.bullish_invalidation?.map((condition, i) => (
                <li key={i}>{condition}</li>
              ))}
            </ul>
          </div>

          <div className="invalidation-card bearish">
            <div className="invalidation-header">
              <TrendingDown size={18} />
              <strong>Bearish Scenario</strong>
            </div>
            <ul>
              {data?.reasoning?.invalidation?.bearish_invalidation?.map((condition, i) => (
                <li key={i}>{condition}</li>
              ))}
            </ul>
          </div>
        </div>

        {data?.reasoning?.invalidation?.key_levels?.length > 0 && (
          <div className="key-levels-section">
            <strong>Key Decision Levels:</strong>
            <div className="levels-list">
              {data.reasoning.invalidation.key_levels.map((level, i) => (
                <span key={i} className="level-badge">{level}</span>
              ))}
            </div>
          </div>
        )}
      </CollapsibleSection>

      {/* Disclaimer */}
      <div className="disclaimer-card">
        <AlertTriangle size={18} />
        <div>
          <strong>Important Disclaimer</strong>
          <p>This analysis is for educational purposes only and should not be considered financial advice. Always conduct your own research and consult with a financial advisor before making trading decisions.</p>
        </div>
      </div>
    </div>
  );
};

// Helper Components
const CollapsibleSection = ({ title, icon, expanded, onToggle, children, badge, badgeColor }) => (
  <div className="collapsible-section">
    <button className="section-header" onClick={onToggle}>
      <div className="section-title">
        <span className="section-icon">{icon}</span>
        <h3>{title}</h3>
        {badge && (
          <span 
            className="section-badge"
            style={badgeColor ? { background: `${badgeColor}20`, color: badgeColor } : {}}
          >
            {badge}
          </span>
        )}
      </div>
      <span className="expand-icon">
        {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </span>
    </button>
    {expanded && <div className="section-content">{children}</div>}
  </div>
);

const InfoCard = ({ label, value }) => {
  // Clean value from any markdown artifacts
  const cleanValue = typeof value === 'string' 
    ? value.replace(/^-\s*\*\*.*?\*\*:\s*/g, '').replace(/\*\*/g, '')
    : value;
    
  return (
    <div className="info-card">
      <span className="info-label">{label}</span>
      <span className="info-value">{cleanValue || 'N/A'}</span>
    </div>
  );
};

export default AnalysisResults;
