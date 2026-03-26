'use client';

import React, { useState, useEffect } from 'react';
import { Activity, History, Tag, Database, Clock, Wifi, WifiOff } from 'lucide-react';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || `${API_BASE_URL.replace(/^http/, 'ws')}/ws/nfc/`;

interface ScanData {
  id?: number;
  uid: string;
  atr?: string;
  timestamp: string;
  status: 'success' | 'error';
  message?: string;
}

export default function Dashboard() {
  const [scans, setScans] = useState<ScanData[]>([]);
  const [currentScan, setCurrentScan] = useState<ScanData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [pulseActive, setPulseActive] = useState(false);
  const [readerStatus, setReaderStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [readerName, setReaderName] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    let ws: WebSocket;

    const connectWS = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('Connected to NFC WebSocket');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'reader_status') {
          const oldStatus = readerStatus;
          setReaderStatus(data.status);
          setReaderName(data.reader_name);
          
          if (data.status === 'connected' && oldStatus !== 'connected') {
            showToast(`Reader Connected: ${data.reader_name}`, 'success');
          } else if (data.status === 'disconnected' && oldStatus === 'connected') {
            showToast('NFC Reader Disconnected!', 'error');
          }
        } else if (data.uid) { // Scan result
          const scanData: ScanData = data;
          setCurrentScan(scanData);
          setScans((prev) => [scanData, ...prev.slice(0, 9)]);
          triggerPulse();
          playBeep();
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setReaderStatus('disconnected');
        console.log('Disconnected from NFC WebSocket');
        setTimeout(connectWS, 3000);
      };
    };

    connectWS();
    fetchHistory();

    return () => ws?.close();
  }, [readerStatus]);

  const fetchHistory = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/api/scans/`);
      const data = await resp.json();
      const results = data.results || data;
      setScans(results);
      if (results.length > 0) setCurrentScan(results[0]);
    } catch (err) {
      console.error('Failed to fetch history', err);
    }
  };

  const toggleListening = async (start: boolean) => {
    const endpoint = start ? 'start' : 'stop';
    try {
      const resp = await fetch(`${API_BASE_URL}/api/${endpoint}/`, { method: 'POST' });
      if (resp.ok) {
        setIsListening(start);
        showToast(`Listener ${start ? 'Started' : 'Stopped'}`, 'success');
      }
    } catch (err) {
      console.error(`Failed to ${endpoint} listening`, err);
      showToast('Backend connection error', 'error');
    }
  };

  const triggerPulse = () => {
    setPulseActive(true);
    setTimeout(() => setPulseActive(false), 1000);
  };

  const playBeep = () => {
    try {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);

      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); 
      gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

      oscillator.start();
      oscillator.stop(audioCtx.currentTime + 0.1);
    } catch (e) { console.error('Audio failed', e); }
  };

  return (
    <>
      <div className={`status-bar ${readerStatus}`}>
        {readerStatus === 'connected' ? (
          <><Wifi size={18} /> NFC Reader Connected: {readerName || 'ACR122U'} ✅</>
        ) : readerStatus === 'connecting' ? (
          <><Activity size={18} className="waiting" /> Detecting NFC Reader... 🟡</>
        ) : (
          <><WifiOff size={18} /> No NFC Reader Detected ❌</>
        )}
      </div>

      <main className="dashboard">
        {toast && (
          <div className="toast">
            {toast.type === 'success' ? <Wifi color="var(--success)" /> : <WifiOff color="var(--error)" />}
            {toast.message}
          </div>
        )}
        
        <header className="header" style={{ marginTop: '1rem' }}>
        <div className="title-group">
          <h1>NFC Live Control</h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>Real-time ACR122U Dashboard</p>
        </div>
        <div className="status-group" style={{ display: 'flex', gap: '1rem' }}>
          <div className="status-badge">
            {isConnected ? (
              <><span className="status-dot online"></span> Server Online</>
            ) : (
              <><span className="status-dot offline"></span> Server Offline</>
            )}
          </div>
          <div className="status-badge">
            {isListening ? (
              <><span className="status-dot waiting"></span> Reader Active</>
            ) : (
              <><span className="status-dot offline"></span> Reader Stopped</>
            )}
          </div>
        </div>
      </header>

      <section className="main-panel">
        <div className={`live-scan-card ${pulseActive ? 'active-border' : ''}`}>
          <div className={`scan-pulse ${pulseActive ? 'active' : ''}`}></div>
          <Activity size={48} color="var(--primary)" style={{ opacity: 0.5 }} />
          
          {currentScan ? (
            <>
              <div className="uid-display">{currentScan.uid}</div>
              <p style={{ color: 'var(--success)', fontWeight: 600 }}>TAG DETECTED</p>
              
              <div className="data-grid">
                <div className="data-item">
                  <label><Database size={12} inline-block /> ATR</label>
                  <div className="value">{currentScan.atr || 'N/A'}</div>
                </div>
                <div className="data-item">
                  <label><Clock size={12} inline-block /> Timestamp</label>
                  <div className="value">{new Date(currentScan.timestamp).toLocaleString()}</div>
                </div>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <Tag size={64} color="var(--card-border)" />
              <p style={{ color: 'var(--text-muted)', marginTop: '1rem', fontSize: '1.25rem' }}>
                Waiting for tap...
              </p>
            </div>
          )}
        </div>

        <div className="controls">
          <button 
            className="btn btn-primary" 
            onClick={() => toggleListening(!isListening)}
          >
            {isListening ? 'Stop Reader' : 'Start Reader'}
          </button>
          <button className="btn btn-secondary" onClick={fetchHistory}>
            Refresh History
          </button>
        </div>
      </section>

      <aside className="history-panel">
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <History size={20} /> History
        </h2>
        {scans.map((scan, i) => (
          <div key={i} className="history-card" onClick={() => setCurrentScan(scan)}>
            <div className="history-header">
              <span className="history-uid">{scan.uid}</span>
              <span className="history-time">{new Date(scan.timestamp).toLocaleTimeString()}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
              ATR: {scan.atr?.substring(0, 20)}...
            </div>
          </div>
        ))}
        {scans.length === 0 && (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>No recent scans</p>
        )}
      </aside>
    </main>
    </>
  );
}
