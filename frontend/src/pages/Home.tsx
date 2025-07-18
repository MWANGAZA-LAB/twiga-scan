import React, { useState, useEffect } from 'react';
import ScanInput from '../components/ScanInput';
import ScanResult, { ScanResultData } from '../components/ScanResult';

const detectProvider = (data: string): string | undefined => {
  // Simple Fedi Wallet detection (customize as needed)
  if (data.includes('fedi') || data.includes('fedimint')) return 'Fedi Wallet';
  return undefined;
};

const mockScan = (data: string): ScanResultData => {
  if (!data) return null as any;
  if (data.startsWith('bitcoin:')) {
    return {
      contentType: 'BIP21',
      parsed: { address: data.slice(8), amount: '0.01', label: 'Demo' },
      provider: 'DemoProvider',
      authStatus: 'Verified',
      warnings: [],
    };
  } else if (data.startsWith('lnbc')) {
    const provider = detectProvider(data) || 'Unknown';
    return {
      contentType: 'BOLT11',
      parsed: { invoice: data, amount: '0.001', description: 'Lightning Invoice' },
      provider,
      authStatus: provider === 'Unknown' ? 'Suspicious' : 'Verified',
      warnings: provider === 'Unknown' ? ['Unknown provider'] : [],
    };
  } else {
    return {
      contentType: 'Unknown',
      parsed: { raw: data },
      provider: undefined,
      authStatus: 'Invalid',
      warnings: ['Unrecognized format'],
    };
  }
};

const Home: React.FC = () => {
  const [scanResult, setScanResult] = useState<ScanResultData | null>(null);
  const [inputData, setInputData] = useState<string>('');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  const [bitcoinPrice, setBitcoinPrice] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const scanName = 'twiga-scan';

  // Fetch Bitcoin price
  useEffect(() => {
    const fetchBitcoinPrice = async () => {
      try {
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');
        const data = await response.json();
        setBitcoinPrice(data.bitcoin.usd);
      } catch (error) {
        console.error('Failed to fetch Bitcoin price:', error);
      }
    };
    fetchBitcoinPrice();
    const interval = setInterval(fetchBitcoinPrice, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const handleScan = (data: string) => {
    setInputData(data);
  };

  const handleVerify = async () => {
    if (!inputData.trim()) {
      alert('Please enter a QR code or URL to verify.');
      return;
    }
    
    setIsLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      const result = mockScan(inputData);
      setScanResult(result);
      setIsLoading(false);
    }, 1000);
  };

  const toggleMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className={`twiga-bg ${isDarkMode ? 'dark-mode' : 'light-mode'}`} style={{ minHeight: '100vh', padding: 20, margin: 0, position: 'relative' }}>
      <div className="twiga-watermark">{scanName}</div>
      
      {/* Main Container */}
      <div className="main-container" style={{
        maxWidth: 800,
        margin: '20px auto',
        padding: 30,
        borderRadius: 20,
        background: isDarkMode ? 'rgba(24, 24, 24, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        border: `2px solid ${isDarkMode ? '#ff9900' : '#ff6600'}`,
        backdropFilter: 'blur(10px)',
      }}>
        
        {/* Header with Mode Toggle */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 30 }}>
          <h2 className="twiga-header">
            <span className="twiga-title">twiga-scan™</span>
            <span className="twiga-catchy">&nbsp;| Bitcoin/Lightning QR & URL Scanner – "Scan with Trust"</span>
          </h2>
          <button
            onClick={toggleMode}
            style={{
              background: isDarkMode ? '#ff9900' : '#ff6600',
              color: isDarkMode ? '#181818' : '#fff',
              border: 'none',
              padding: '10px 20px',
              borderRadius: 25,
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 14,
            }}
          >
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>

        {/* Bitcoin Price Display */}
        {bitcoinPrice && (
          <div style={{
            background: isDarkMode ? '#232323' : '#f5f5f5',
            padding: 15,
            borderRadius: 12,
            marginBottom: 20,
            textAlign: 'center',
            border: `1px solid ${isDarkMode ? '#ff9900' : '#ff6600'}`,
          }}>
            <div style={{ color: isDarkMode ? '#ff9900' : '#ff6600', fontWeight: 600, fontSize: 18 }}>
              ₿ Bitcoin Price: ${bitcoinPrice.toLocaleString()} USD
            </div>
          </div>
        )}

        {/* Security Information */}
        <div style={{
          background: isDarkMode ? '#1a1a1a' : '#fff3cd',
          padding: 15,
          borderRadius: 12,
          marginBottom: 20,
          border: `1px solid ${isDarkMode ? '#ff3b3b' : '#ffc107'}`,
        }}>
          <h4 style={{ color: isDarkMode ? '#ff3b3b' : '#856404', marginBottom: 10 }}>
            🔒 Security Notice
          </h4>
          <ul style={{ color: isDarkMode ? '#ccc' : '#856404', fontSize: 14, margin: 0, paddingLeft: 20 }}>
            <li>Always verify the source before making any Bitcoin payments</li>
            <li>Check the provider and amount carefully</li>
            <li>Never share your private keys or seed phrases</li>
            <li>This tool helps verify legitimacy but always double-check</li>
          </ul>
        </div>

        {/* Input Section */}
        <ScanInput onScan={handleScan} isDarkMode={isDarkMode} />
        
        {/* Verify Button */}
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <button
            onClick={handleVerify}
            disabled={isLoading || !inputData.trim()}
            style={{
              background: isLoading || !inputData.trim() ? '#666' : '#ff9900',
              color: '#181818',
              border: 'none',
              padding: '12px 30px',
              borderRadius: 25,
              cursor: isLoading || !inputData.trim() ? 'not-allowed' : 'pointer',
              fontWeight: 600,
              fontSize: 16,
              minWidth: 120,
            }}
          >
            {isLoading ? '🔍 Verifying...' : '🔍 Verify & Scan'}
          </button>
        </div>

        {/* Result Section */}
        <ScanResult result={scanResult} isDarkMode={isDarkMode} />
      </div>
    </div>
  );
};

export default Home; 