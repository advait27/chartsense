import React, { useState } from 'react';
import { Calculator, DollarSign, Info } from 'lucide-react';
import './RiskCalculator.css';

const RiskCalculator = () => {
  const [accountSize, setAccountSize] = useState('');
  const [riskPercentage, setRiskPercentage] = useState('2');
  const [entryPrice, setEntryPrice] = useState('');
  const [stopLoss, setStopLoss] = useState('');
  const [results, setResults] = useState(null);

  const calculateRisk = (e) => {
    e.preventDefault();

    const account = parseFloat(accountSize);
    const risk = parseFloat(riskPercentage);
    const entry = parseFloat(entryPrice);
    const sl = parseFloat(stopLoss);

    if (!account || !risk || !entry || !sl) {
      alert('Please fill in all fields with valid numbers');
      return;
    }

    // Calculate risk amount
    const riskAmount = (account * risk) / 100;

    // Calculate pips/points at risk
    const pipsAtRisk = Math.abs(entry - sl);
    
    // Calculate position size (simplified - for forex with standard lot)
    // For more accurate calculation, would need to know pip value
    const pipValue = 10; // Assuming standard lot for major pairs
    const positionSize = riskAmount / (pipsAtRisk * pipValue);

    // Calculate potential reward (assuming 1:2 risk-reward)
    const takeProfit1 = entry + (pipsAtRisk * 2 * (entry > sl ? 1 : -1));
    const potentialReward = riskAmount * 2;

    setResults({
      riskAmount: riskAmount.toFixed(2),
      pipsAtRisk: pipsAtRisk.toFixed(1),
      positionSize: positionSize.toFixed(2),
      potentialReward: potentialReward.toFixed(2),
      takeProfit: takeProfit1.toFixed(5)
    });
  };

  return (
    <div className="risk-calculator">
      <div className="calculator-header">
        <Calculator size={24} />
        <h3 className="calculator-title">Risk Calculator</h3>
      </div>

      <form className="calculator-form" onSubmit={calculateRisk}>
        <div className="form-group">
          <label className="form-label">Account Size ($)</label>
          <input
            type="number"
            className="form-input"
            value={accountSize}
            onChange={(e) => setAccountSize(e.target.value)}
            placeholder="e.g., 10000"
            step="0.01"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Risk Per Trade (%)</label>
          <input
            type="number"
            className="form-input"
            value={riskPercentage}
            onChange={(e) => setRiskPercentage(e.target.value)}
            placeholder="e.g., 2"
            step="0.1"
            max="10"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Entry Price</label>
          <input
            type="number"
            className="form-input"
            value={entryPrice}
            onChange={(e) => setEntryPrice(e.target.value)}
            placeholder="e.g., 1.0850"
            step="0.00001"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Stop Loss Price</label>
          <input
            type="number"
            className="form-input"
            value={stopLoss}
            onChange={(e) => setStopLoss(e.target.value)}
            placeholder="e.g., 1.0800"
            step="0.00001"
          />
        </div>

        <button type="submit" className="calculate-btn">
          <Calculator size={20} />
          Calculate Risk
        </button>
      </form>

      {results && (
        <div className="results-grid">
          <div className="result-card">
            <div className="result-label">Risk Amount</div>
            <div className="result-value large">
              <DollarSign size={24} style={{ display: 'inline', marginBottom: '-4px' }} />
              {results.riskAmount}
            </div>
          </div>

          <div className="result-card">
            <div className="result-label">Pips at Risk</div>
            <div className="result-value">{results.pipsAtRisk}</div>
          </div>

          <div className="result-card">
            <div className="result-label">Position Size (lots)</div>
            <div className="result-value">{results.positionSize}</div>
          </div>

          <div className="result-card">
            <div className="result-label">Potential Reward (1:2)</div>
            <div className="result-value large">
              <DollarSign size={24} style={{ display: 'inline', marginBottom: '-4px' }} />
              {results.potentialReward}
            </div>
          </div>

          <div className="result-card" style={{ gridColumn: 'span 2' }}>
            <div className="result-label">Suggested Take Profit (1:2)</div>
            <div className="result-value">{results.takeProfit}</div>
          </div>
        </div>
      )}

      <div className="info-note">
        <Info size={16} />
        Calculator uses standard forex lot assumptions. Adjust for your specific instrument.
      </div>
    </div>
  );
};

export default RiskCalculator;
