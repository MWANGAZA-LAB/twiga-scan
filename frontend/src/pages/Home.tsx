import React, { useState, useEffect } from 'react';
import ScanInput from '../components/ScanInput';
import ScanResult from '../components/ScanResult';
import { apiService, ScanResponse } from '../services/api';

interface BitcoinPrice {
  usd: number;
  usd_24h_change: number;
}

const Home: React.FC = () => {
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bitcoinPrice, setBitcoinPrice] = useState<BitcoinPrice | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
    fetchBitcoinPrice();
  }, []);

  const checkBackendConnection = async () => {
    try {
      await apiService.healthCheck();
      setBackendStatus('connected');
    } catch (error) {
      console.error('Backend connection failed:', error);
      setBackendStatus('disconnected');
    }
  };

  const fetchBitcoinPrice = async () => {
    try {
      const response = await fetch(
        'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true'
      );
      const data = await response.json();
      setBitcoinPrice(data.bitcoin);
    } catch (error) {
      console.error('Failed to fetch Bitcoin price:', error);
    }
  };

  const handleScan = async (content: string) => {
    if (!content.trim()) {
      setError('Please enter QR code content or URL');
      return;
    }

    setIsLoading(true);
    setError(null);
    setScanResult(null);

    try {
      // Generate a simple device ID (in production, this would be more sophisticated)
      const deviceId = `web-${navigator.userAgent.slice(0, 50)}`;
      
      const result = await apiService.scanContent({
        content: content.trim(),
        device_id: deviceId,
        ip_address: '127.0.0.1' // In production, get real IP
      });

      setScanResult(result);
    } catch (error) {
      console.error('Scan failed:', error);
      setError(error instanceof Error ? error.message : 'Failed to scan content');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!scanResult) return;
    
    try {
      await apiService.updateScanAction(scanResult.scan_id, {
        action: 'approved',
        outcome: 'User verified and approved'
      });
      
      // Update the local state to reflect the action
      setScanResult(prev => prev ? {
        ...prev,
        user_action: 'approved',
        outcome: 'User verified and approved'
      } : null);
      
    } catch (error) {
      console.error('Failed to update scan action:', error);
      setError('Failed to record verification action');
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDarkMode 
        ? 'bg-gray-900 text-white' 
        : 'bg-gradient-to-br from-orange-50 to-yellow-50 text-gray-900'
    }`}>
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="text-3xl font-bold text-orange-600">🦒</div>
            <div>
              <h1 className="text-2xl font-bold">Twiga Scan</h1>
              <p className="text-sm opacity-75">Bitcoin & Lightning Authentication</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Backend Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                backendStatus === 'connected' ? 'bg-green-500' :
                backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
              }`}></div>
              <span className="text-sm">
                {backendStatus === 'connected' ? 'Backend Connected' :
                 backendStatus === 'disconnected' ? 'Backend Disconnected' : 'Checking...'}
              </span>
            </div>

            {/* Bitcoin Price */}
            {bitcoinPrice && (
              <div className="text-sm">
                <span className="font-semibold">₿ ${bitcoinPrice.usd.toLocaleString()}</span>
                <span className={`ml-2 ${
                  bitcoinPrice.usd_24h_change >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {bitcoinPrice.usd_24h_change >= 0 ? '↗' : '↘'} 
                  {Math.abs(bitcoinPrice.usd_24h_change).toFixed(2)}%
                </span>
              </div>
            )}

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-lg transition-colors ${
                isDarkMode 
                  ? 'bg-gray-700 hover:bg-gray-600' 
                  : 'bg-white hover:bg-gray-100 shadow-md'
              }`}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 pb-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Scan Input */}
          <ScanInput onScan={handleScan} isLoading={isLoading} />

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Scan Result */}
          {scanResult && (
            <div className="space-y-4">
              <ScanResult result={scanResult} />
              
              {/* Verify Button */}
              <div className="flex justify-center">
                <button
                  onClick={handleVerify}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg transition-colors shadow-lg"
                >
                  ✅ Verify & Approve
                </button>
              </div>
            </div>
          )}

          {/* Security Information */}
          <div className={`mt-8 p-6 rounded-lg ${
            isDarkMode 
              ? 'bg-gray-800 border border-gray-700' 
              : 'bg-white border border-gray-200 shadow-lg'
          }`}>
            <h3 className="text-lg font-semibold mb-4">🔒 Security Information</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">What we verify:</h4>
                <ul className="space-y-1 opacity-75">
                  <li>• Cryptographic signature validity</li>
                  <li>• Domain and SSL certificate checks</li>
                  <li>• Known provider identification</li>
                  <li>• Format and structure validation</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Best practices:</h4>
                <ul className="space-y-1 opacity-75">
                  <li>• Always verify the amount before sending</li>
                  <li>• Check the recipient address carefully</li>
                  <li>• Use trusted wallets and services</li>
                  <li>• Keep your private keys secure</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home; 