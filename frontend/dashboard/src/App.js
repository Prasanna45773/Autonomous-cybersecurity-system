import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Area, AreaChart
} from 'recharts';
import { 
  Activity, Shield, AlertTriangle, CheckCircle, Ban, Server,
  Brain, Target, TrendingUp, Zap, Eye, EyeOff, Download,
  Cpu, HardDrive, Network, Clock, Lock, Unlock
} from 'lucide-react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const API = 'http://localhost:5000/api';

function App() {
  const [status, setStatus] = useState(null);
  const [monitoring, setMonitoring] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [detections, setDetections] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [blockedIPs, setBlockedIPs] = useState([]);
  const [isolatedHosts, setIsolatedHosts] = useState([]);
  
  const [threatTrend, setThreatTrend] = useState([]);
  const [view, setView] = useState('overview');

  // Add after existing state declarations
  const [cryptoStats, setCryptoStats] = useState(null);
  
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (monitoring) {
      fetchMetrics();
      fetchDetections();
      fetchCryptoStats();
      const i1 = setInterval(fetchMetrics, 5000);
      const i2 = setInterval(fetchDetections, 2000);
      const i3 = setInterval(fetchCryptoStats, 5000);
      return () => { clearInterval(i1); clearInterval(i2); clearInterval(i3); };
    }
  }, [monitoring]);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API}/status`);
      setStatus(res.data);
      setMonitoring(res.data.autonomous_loop_active);
      setLoading(false);
    } catch (error) {
      console.error(error);
      toast.error('Connection failed');
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`${API}/metrics`);
      setMetrics(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchCryptoStats = async () => {
  try {
    const res = await axios.get(`${API}/crypto/stats`);
    setCryptoStats(res.data);
  } catch (error) {
    console.error(error);
  }
};

  const fetchDetections = async () => {
    try {
      const res = await axios.get(`${API}/detections`);
      setDetections(prev => [...res.data, ...prev].slice(0, 50));
      
      const blocked = await axios.get(`${API}/blocked-ips`);
      setBlockedIPs(blocked.data.blocked_ips);
      setIsolatedHosts(blocked.data.isolated_hosts);
      
      // Update trend
      if (res.data.length > 0) {
        const latest = res.data[0];
        setThreatTrend(prev => [...prev, {
          time: new Date().toLocaleTimeString(),
          threats: latest.prediction === 'attack' ? 1 : 0,
          confidence: (latest.confidence * 100).toFixed(1)
        }].slice(-30));
      }
      
      // Show alerts for high-risk threats
      res.data.forEach(d => {
        if (d.decision?.risk_level === 'high') {
          toast.error(`🚨 HIGH RISK: ${d.traffic_data.src_ip}`, {toastId: d.cycle});
        }
      });
    } catch (error) {
      console.error(error);
    }
  };

  const startMonitoring = async () => {
    try {
      await axios.post(`${API}/start-monitoring`);
      setMonitoring(true);
      toast.success('✅ Autonomous monitoring started!');
    } catch (error) {
      toast.error('Cannot start - models not trained');
    }
  };

  const stopMonitoring = async () => {
    try {
      await axios.post(`${API}/stop-monitoring`);
      setMonitoring(false);
      toast.info('⏹️ Monitoring stopped');
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <Activity size={64} className="spin" />
        <h2>Initializing System</h2>
        <p>Loading AI models...</p>
      </div>
    );
  }

  const stats = detections.reduce((acc, d) => {
    if (d.prediction === 'attack') {
      acc.threats++;
      acc[d.decision?.risk_level || 'low']++;
    } else {
      acc.normal++;
    }
    return acc;
  }, { threats: 0, normal: 0, low: 0, medium: 0, high: 0 });

  const pieData = [
    { name: 'Normal', value: stats.normal, color: '#10b981' },
    { name: 'Threats', value: stats.threats, color: '#ef4444' }
  ];

  const riskData = [
    { risk: 'Low', count: stats.low, fill: '#fbbf24' },
    { risk: 'Med', count: stats.medium, fill: '#f97316' },
    { risk: 'High', count: stats.high, fill: '#ef4444' }
  ];

  return (
    <div className="app">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <Shield size={36} className="pulse" />
          <div>
            <h1>Autonomous Cybersecurity AI</h1>
            <p className="subtitle">Multi-Agent Reinforcement Learning System</p>
          </div>
          <div className="badges">
            <div className={`badge ${status?.status === 'ready' ? 'ready' : 'init'}`}>
              <div className="dot" />
              {status?.status || 'unknown'}
            </div>
            <div className="badge learning">
              <Brain size={16} />
              Learning Active
            </div>
          </div>
        </div>
      </header>

      {/* Nav */}
      <nav className="nav">
        <button className={view === 'overview' ? 'active' : ''} onClick={() => setView('overview')}>
          <Activity size={18} /> Overview
        </button>
        <button className={view === 'detections' ? 'active' : ''} onClick={() => setView('detections')}>
          <Target size={18} /> Detections
        </button>
        <button className={view === 'learning' ? 'active' : ''} onClick={() => setView('learning')}>
          <Brain size={18} /> Learning
        </button>
        <button className={view === 'system' ? 'active' : ''} onClick={() => setView('system')}>
          <Server size={18} /> System
        </button>
        <button className={view === 'crypto' ? 'active' : ''} onClick={() => setView('crypto')}>
          <Lock size={18} /> Cryptography
        </button>
      </nav>

      <main className="main">
        {/* Controls */}
        <div className="card controls">
          <h2>System Controls</h2>
          <div className="btn-group">
            <button 
              onClick={monitoring ? stopMonitoring : startMonitoring}
              className={`btn ${monitoring ? 'danger' : 'primary'}`}
              disabled={!status?.models_trained}
            >
              {monitoring ? <><EyeOff size={18} /> Stop</> : <><Eye size={18} /> Start</>}
            </button>
            {!status?.models_trained && (
              <div className="warning">
                <AlertTriangle size={18} />
                Models training... Please wait
              </div>
            )}
          </div>
        </div>

        {/* Overview */}
        {view === 'overview' && (
          <>
            <div className="stats">
              <div className="stat green">
                <CheckCircle size={32} />
                <div>
                  <div className="label">Normal Traffic</div>
                  <div className="value">{stats.normal}</div>
                  <div className="sub">{((stats.normal/(stats.normal+stats.threats)||0)*100).toFixed(1)}%</div>
                </div>
              </div>

              <div className="stat red">
                <AlertTriangle size={32} />
                <div>
                  <div className="label">Threats Detected</div>
                  <div className="value">{status?.total_threats_detected || 0}</div>
                  <div className="sub">High: {stats.high} | Med: {stats.medium}</div>
                </div>
              </div>

              <div className="stat blue">
                <Ban size={32} />
                <div>
                  <div className="label">Blocked IPs</div>
                  <div className="value">{blockedIPs.length}</div>
                  <div className="sub">Isolated: {isolatedHosts.length}</div>
                </div>
              </div>

              <div className="stat purple">
                <Brain size={32} />
                <div>
                  <div className="label">Learning Accuracy</div>
                  <div className="value">
                    {((status?.learning_metrics?.accuracy || 0) * 100).toFixed(1)}%
                  </div>
                  <div className="sub">Auto-Learn: {status?.auto_learning_events || 0}</div>
                </div>
              </div>
            </div>

            <div className="charts">
              <div className="card">
                <h3>Traffic Distribution</h3>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      label={({name, percent}) => `${name}: ${(percent*100).toFixed(0)}%`}
                      outerRadius={90}
                      dataKey="value"
                    >
                      {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h3>Threat Trend</h3>
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={threatTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" tick={{fontSize: 10}} />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{background: '#1e293b', border: '1px solid #334155'}} />
                    <Area type="monotone" dataKey="confidence" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h3>Risk Distribution</h3>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={riskData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="risk" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{background: '#1e293b', border: '1px solid #334155'}} />
                    <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                      {riskData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

        {/* Detections */}
        {view === 'detections' && (
          <>
            <div className="card">
              <h3>Real-Time Detection Events</h3>
              <div className="detections">
                {detections.slice(0, 15).map((d, i) => (
                  <div key={i} className={`detection ${d.prediction === 'attack' ? 'threat' : 'normal'}`}>
                    <div className="det-main">
                      <div className="det-time">
                        <Clock size={14} />
                        {new Date(d.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="det-ips">
                        <Network size={14} />
                        <span>{d.traffic_data.src_ip}</span>
                        <span>→</span>
                        <span>{d.traffic_data.dst_ip}</span>
                      </div>
                      <div className="det-result">
                        {d.prediction === 'attack' ? (
                          <>
                            <AlertTriangle size={18} />
                            <span className="threat-text">
                              {d.decision?.risk_level?.toUpperCase()} RISK
                            </span>
                            <span className="conf">{(d.confidence * 100).toFixed(1)}%</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle size={18} />
                            <span>Normal</span>
                            <span className="conf green">{(d.confidence * 100).toFixed(1)}%</span>
                          </>
                        )}
                      </div>
                    </div>
                    {d.prediction === 'attack' && (
                      <div className="det-details">
                        <div><Zap size={14} /> Actions: {d.decision?.actions?.join(', ')}</div>
                        <div><Brain size={14} /> AI Action: {d.learning_action}</div>
                        <div><TrendingUp size={14} /> Reward: {d.reward}</div>
                      </div>
                    )}
                  </div>
                ))}
                {detections.length === 0 && (
                  <div className="empty">
                    <Activity size={48} />
                    <p>No detections yet. Start monitoring.</p>
                  </div>
                )}
              </div>
            </div>

            <div className="grid-2">
              {blockedIPs.length > 0 && (
                <div className="card">
                  <h3><Lock size={20} /> Blocked IPs ({blockedIPs.length})</h3>
                  <div className="ip-grid">
                    {blockedIPs.map((ip, i) => (
                      <div key={i} className="ip-badge blocked">
                        <Ban size={14} />
                        {ip}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {isolatedHosts.length > 0 && (
                <div className="card">
                  <h3><Shield size={20} /> Isolated Hosts ({isolatedHosts.length})</h3>
                  <div className="ip-grid">
                    {isolatedHosts.map((h, i) => (
                      <div key={i} className="ip-badge isolated">
                        <Shield size={14} />
                        {h}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Learning */}
        {view === 'learning' && (
          <>
            <div className="stats">
              <div className="stat purple">
                <Brain size={32} />
                <div>
                  <div className="label">Accuracy</div>
                  <div className="value">
                    {((status?.learning_metrics?.accuracy || 0) * 100).toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="stat blue">
                <TrendingUp size={32} />
                <div>
                  <div className="label">Avg Reward</div>
                  <div className="value">
                    {status?.learning_metrics?.average_reward?.toFixed(2) || '0.00'}
                  </div>
                </div>
              </div>

              <div className="stat yellow">
                <Target size={32} />
                <div>
                  <div className="label">Exploration Rate</div>
                  <div className="value">
                    {((status?.learning_metrics?.exploration_rate || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="stat green">
                <Zap size={32} />
                <div>
                  <div className="label">Auto-Learning</div>
                  <div className="value">{status?.auto_learning_events || 0}</div>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Reinforcement Learning Status</h3>
              <div className="learning-grid">
                <div className="learn-box">
                  <div className="learn-label">Q-Table Size</div>
                  <div className="learn-value">{status?.learning_metrics?.q_table_size || 0}</div>
                  <p>Learned state-action pairs</p>
                </div>
                <div className="learn-box">
                  <div className="learn-label">Total Feedback</div>
                  <div className="learn-value">{status?.learning_metrics?.total_feedback || 0}</div>
                  <p>Learning iterations</p>
                </div>
                <div className="learn-box">
                  <div className="learn-label">Exploitation</div>
                  <div className="learn-value">
                    {(100 - (status?.learning_metrics?.exploration_rate || 0) * 100).toFixed(1)}%
                  </div>
                  <p>Using learned knowledge</p>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Closed-Loop Operation</h3>
              <div className="loop-diagram">
                <div className="loop-step">
                  <Eye size={32} />
                  <h4>Observe</h4>
                  <p>Monitor network traffic continuously</p>
                </div>
                <div className="arrow">→</div>
                <div className="loop-step">
                  <Target size={32} />
                  <h4>Detect</h4>
                  <p>ML models identify threats</p>
                </div>
                <div className="arrow">→</div>
                <div className="loop-step">
                  <Brain size={32} />
                  <h4>Decide</h4>
                  <p>AI selects optimal action</p>
                </div>
                <div className="arrow">→</div>
                <div className="loop-step">
                  <Zap size={32} />
                  <h4>Act</h4>
                  <p>Execute response automatically</p>
                </div>
                <div className="arrow">→</div>
                <div className="loop-step">
                  <TrendingUp size={32} />
                  <h4>Learn</h4>
                  <p>Update Q-table from outcomes</p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* System */}
        {view === 'system' && metrics && (
          <>
            <div className="stats">
              <div className="stat">
                <Cpu size={32} />
                <div>
                  <div className="label">CPU Usage</div>
                  <div className="value">{metrics.system?.cpu_percent?.toFixed(1) || 0}%</div>
                </div>
              </div>

              <div className="stat">
                <HardDrive size={32} />
                <div>
                  <div className="label">Memory</div>
                  <div className="value">{metrics.system?.memory_percent?.toFixed(1) || 0}%</div>
                </div>
              </div>

              <div className="stat">
                <Network size={32} />
                <div>
                  <div className="label">Connections</div>
                  <div className="value">{metrics.system?.network_connections || 0}</div>
                </div>
              </div>

              <div className="stat">
                <Activity size={32} />
                <div>
                  <div className="label">Total Actions</div>
                  <div className="value">{status?.total_actions_taken || 0}</div>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Detection Statistics</h3>
              <div className="stats-table">
                <div className="stat-row">
                  <span>Total Threats Detected:</span>
                  <strong>{metrics.detection_stats?.total_threats || 0}</strong>
                </div>
                <div className="stat-row">
                  <span>Total Actions Taken:</span>
                  <strong>{metrics.detection_stats?.total_actions || 0}</strong>
                </div>
                <div className="stat-row">
                  <span>False Positives:</span>
                  <strong className="red">{metrics.detection_stats?.false_positives || 0}</strong>
                </div>
                <div className="stat-row">
                  <span>False Negatives:</span>
                  <strong className="red">{metrics.detection_stats?.false_negatives || 0}</strong>
                </div>
                <div className="stat-row">
                  <span>Auto-Learning Events:</span>
                  <strong className="green">{metrics.detection_stats?.auto_learning_events || 0}</strong>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Model Performance</h3>
              {status?.model_metrics && (
                <div className="metrics-grid">
                  <div className="metric-box">
                    <div className="metric-label">Accuracy</div>
                    <div className="metric-value">{(status.model_metrics.accuracy * 100).toFixed(2)}%</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-label">Precision</div>
                    <div className="metric-value">{(status.model_metrics.precision * 100).toFixed(2)}%</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-label">Recall</div>
                    <div className="metric-value">{(status.model_metrics.recall * 100).toFixed(2)}%</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-label">F1-Score</div>
                    <div className="metric-value">{(status.model_metrics.f1_score * 100).toFixed(2)}%</div>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

      {/* Cryptography View */}
{view === 'crypto' && cryptoStats && (
  <>
    <div className="stats">
      <div className="stat purple">
        <Lock size={32} />
        <div>
          <div className="label">Total Operations</div>
          <div className="value">{cryptoStats.total_operations || 0}</div>
          <div className="sub">Cryptographic operations</div>
        </div>
      </div>

      <div className="stat blue">
        <Shield size={32} />
        <div>
          <div className="label">Encryption Status</div>
          <div className="value">{cryptoStats.encryption_enabled ? 'ACTIVE' : 'INACTIVE'}</div>
          <div className="sub">AES-256-GCM</div>
        </div>
      </div>

      <div className="stat green">
        <CheckCircle size={32} />
        <div>
          <div className="label">Key Strength</div>
          <div className="value">{cryptoStats.key_strength?.split('/')[0] || 'RSA-2048'}</div>
          <div className="sub">Asymmetric encryption</div>
        </div>
      </div>

      <div className="stat yellow">
        <Zap size={32} />
        <div>
          <div className="label">Signatures</div>
          <div className="value">{cryptoStats.operations_breakdown?.sign || 0}</div>
          <div className="sub">Digital signatures created</div>
        </div>
      </div>
    </div>

    <div className="card">
      <h3><Lock size={20} /> Cryptographic Operations Breakdown</h3>
      <div className="crypto-breakdown">
        <div className="crypto-item">
          <div className="crypto-icon encrypt">🔒</div>
          <div className="crypto-details">
            <div className="crypto-label">Encryption Operations</div>
            <div className="crypto-value">{cryptoStats.operations_breakdown?.encrypt || 0}</div>
            <p>AES-256-GCM encrypted data blocks</p>
          </div>
        </div>

        <div className="crypto-item">
          <div className="crypto-icon decrypt">🔓</div>
          <div className="crypto-details">
            <div className="crypto-label">Decryption Operations</div>
            <div className="crypto-value">{cryptoStats.operations_breakdown?.decrypt || 0}</div>
            <p>Successfully decrypted data blocks</p>
          </div>
        </div>

        <div className="crypto-item">
          <div className="crypto-icon sign">✍️</div>
          <div className="crypto-details">
            <div className="crypto-label">Digital Signatures</div>
            <div className="crypto-value">{cryptoStats.operations_breakdown?.sign || 0}</div>
            <p>RSA-PSS-SHA256 signatures created</p>
          </div>
        </div>

        <div className="crypto-item">
          <div className="crypto-icon key">🔑</div>
          <div className="crypto-details">
            <div className="crypto-label">Key Exchanges</div>
            <div className="crypto-value">{cryptoStats.operations_breakdown?.key_exchange || 0}</div>
            <p>Secure key exchange operations</p>
          </div>
        </div>
      </div>
    </div>

    <div className="card">
      <h3><Shield size={20} /> Security Architecture</h3>
      <div className="security-grid">
        <div className="security-box">
          <h4>🔐 Data at Rest</h4>
          <p><strong>Algorithm:</strong> AES-256-GCM</p>
          <p><strong>Key Derivation:</strong> PBKDF2-SHA256</p>
          <p><strong>Iterations:</strong> 100,000</p>
          <p><strong>Purpose:</strong> Q-table & logs encryption</p>
        </div>

        <div className="security-box">
          <h4>🔒 Data in Transit</h4>
          <p><strong>Algorithm:</strong> RSA-2048</p>
          <p><strong>Padding:</strong> OAEP-SHA256</p>
          <p><strong>Purpose:</strong> Agent communication</p>
        </div>

        <div className="security-box">
          <h4>✍️ Digital Signatures</h4>
          <p><strong>Algorithm:</strong> RSA-PSS</p>
          <p><strong>Hash:</strong> SHA-256</p>
          <p><strong>Purpose:</strong> Action verification</p>
        </div>

        <div className="security-box">
          <h4>🔑 Key Management</h4>
          <p><strong>Master Key:</strong> 256-bit derived</p>
          <p><strong>Key Pair:</strong> RSA-2048</p>
          <p><strong>Storage:</strong> In-memory (secure)</p>
        </div>
      </div>
    </div>

    <div className="card">
      <h3>🔐 Encrypted Data Flow</h3>
      <div className="crypto-flow">
        <div className="flow-step">
          <div className="flow-icon">📊</div>
          <div className="flow-content">
            <h4>1. Data Collection</h4>
            <p>Monitoring agent collects network traffic</p>
          </div>
        </div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">
          <div className="flow-icon">🔒</div>
          <div className="flow-content">
            <h4>2. Encryption</h4>
            <p>AES-256-GCM encrypts sensitive data</p>
          </div>
        </div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">
          <div className="flow-icon">🧠</div>
          <div className="flow-content">
            <h4>3. Processing</h4>
            <p>ML models analyze encrypted traffic</p>
          </div>
        </div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">
          <div className="flow-icon">✍️</div>
          <div className="flow-content">
            <h4>4. Signing</h4>
            <p>Actions digitally signed for verification</p>
          </div>
        </div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">
          <div className="flow-icon">💾</div>
          <div className="flow-content">
            <h4>5. Secure Storage</h4>
            <p>Encrypted Q-table saved to disk</p>
          </div>
        </div>
      </div>
    </div>

    {cryptoStats.last_operation && (
      <div className="card">
        <h3>🕐 Last Cryptographic Operation</h3>
        <div className="last-crypto-op">
          <div className="op-detail">
            <span className="op-label">Operation:</span>
            <span className="op-value">{cryptoStats.last_operation.operation}</span>
          </div>
          <div className="op-detail">
            <span className="op-label">Algorithm:</span>
            <span className="op-value">{cryptoStats.last_operation.algorithm}</span>
          </div>
          <div className="op-detail">
            <span className="op-label">Timestamp:</span>
            <span className="op-value">{new Date(cryptoStats.last_operation.timestamp).toLocaleString()}</span>
          </div>
          {cryptoStats.last_operation.data_size && (
            <div className="op-detail">
              <span className="op-label">Data Size:</span>
              <span className="op-value">{cryptoStats.last_operation.data_size} bytes</span>
            </div>
          )}
        </div>
      </div>
     )}
    </>
  )}  
      </main>
    </div>
  );
}

export default App;