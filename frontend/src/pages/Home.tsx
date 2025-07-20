import React, { useState, useEffect } from 'react';
import ScanInput from '../components/ScanInput';
import ScanResult from '../components/ScanResult';
import { apiService, ScanResponse } from '../services/api';

const LIGHTNING_WALLETS = [
  { name: 'Fedi', url: 'https://fedi.xyz', color: 'bg-[#1a1a1a]' },
  { name: 'Blink', url: 'https://blink.sv', color: 'bg-blue-900' },
  { name: 'Wallet of Satoshi', url: 'https://walletofsatoshi.com', color: 'bg-black' },
];
const SAVE_SERVICES = [
  { name: 'Bitsacco', url: 'https://bitsacco.com', color: 'bg-orange-700' },
];

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
  const [scanInputKey, setScanInputKey] = useState(0);

  useEffect(() => {
    fetchBitcoinPrice();
  }, []);

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
      const deviceId = `web-${navigator.userAgent.slice(0, 50)}`;
      const result = await apiService.scanContent({
        content: content.trim(),
        device_id: deviceId,
        ip_address: '127.0.0.1',
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
        outcome: 'User verified and approved',
      });
      setScanResult(prev => prev ? {
        ...prev,
        user_action: 'approved',
        outcome: 'User verified and approved',
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
    <div className="min-h-screen bg-gray-100 dark:bg-gray-800 transition-colors duration-300">
      {/* Header/Branding at top left */}
      <header className="flex items-center px-8 py-6">
        <span className="text-4xl text-bitcoin mr-3">🦒</span>
        <div>
          <h1 className="text-2xl font-bold">Twiga Scan</h1>
          <p className="text-sm opacity-75">Bitcoin & Lightning Authentication</p>
        </div>
        <div className="ml-auto flex items-center gap-4">
          {bitcoinPrice && (
            <div className="text-lg font-bold text-green-600">
              ₿ {bitcoinPrice.usd.toLocaleString()}
            </div>
          )}
          <button
            onClick={toggleDarkMode}
            className={`px-4 py-2 font-bold border-2 ${
              isDarkMode
                ? 'bg-bitcoin text-black border-bitcoin-glow'
                : 'bg-white text-bitcoin border-bitcoin'
            }`}
          >
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="container mx-auto px-4 pb-8 flex flex-col items-center">
        {/* Main Twiga Scan Card - no rounded, no shadow, compact */}
        <div className="w-full max-w-xl mt-6">
          <ScanInput key={scanInputKey} onScan={handleScan} isLoading={isLoading} isDarkMode={isDarkMode} />
        </div>

        {/* Show only if there's a result or error */}
        {(error || scanResult) && (
          <div
            className={`border border-bitcoin-glow bg-white dark:bg-gray-900 p-4 mx-auto my-8 w-full max-w-xl ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}
          >
            {error && (
              <>
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3">
                  <strong>Error:</strong> {error}
                </div>
                <div className="flex justify-center mt-4">
                  <button
                    onClick={() => { setScanResult(null); setError(null); setScanInputKey(prev => prev + 1); }}
                    className="font-bold py-3 px-8 transition-colors bg-blue-500 hover:bg-blue-600 text-white"
                    title="Clear scan and start a new scan"
                  >
                    🔄 Refresh
                  </button>
                </div>
              </>
            )}
            {scanResult && (
              <div className="space-y-4">
                <ScanResult result={scanResult} />
                <div className="flex justify-center gap-4">
                  <button
                    onClick={handleVerify}
                    disabled={scanResult.auth_status !== 'Verified'}
                    title={scanResult.auth_status !== 'Verified' ? 'You can only approve results that are fully verified. Suspicious or invalid scans cannot be approved.' : ''}
                    className={`font-bold py-3 px-8 transition-colors
                      ${scanResult.auth_status === 'Verified'
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gray-400 text-gray-200 cursor-not-allowed'}`}
                  >
                    ✅ Verify & Approve
                  </button>
                  <button
                    onClick={() => { setScanResult(null); setError(null); setScanInputKey(prev => prev + 1); }}
                    className="font-bold py-3 px-8 transition-colors bg-blue-500 hover:bg-blue-600 text-white"
                    title="Clear scan and start a new scan"
                  >
                    🔄 Refresh
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Example Inputs */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 w-full max-w-2xl mb-8">
          <h3 className="font-medium text-gray-900 mb-2">💡 Example Inputs:</h3>
          <div className="grid md:grid-cols-2 gap-2 text-sm">
            <div>
              <strong>Bitcoin URI:</strong>
              <code className="block bg-white p-2 rounded mt-1 text-xs break-all">
                bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001
              </code>
            </div>
            <div>
              <strong>Lightning Address:</strong>
              <code className="block bg-white p-2 rounded mt-1 text-xs">
                user@strike.me
              </code>
            </div>
          </div>
        </div>

        {/* Error Display (if not in card) */}
        {/* Security Information */}
        <div className={`mt-8 p-6 rounded-lg w-full max-w-2xl ${
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

        {/* Lightning Wallets Card (supporting feature) */}
        <div className="bg-white dark:bg-[#232323] rounded-xl shadow-lg p-6 mt-8 w-full max-w-lg border border-gray-200 dark:border-bitcoin-glow">
          <div className="flex justify-between items-center mb-2">
            <span className="font-semibold text-lg">Get Your Lightning Address</span>
          </div>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            You will need a Lightning-enabled wallet to receive Bitcoin
          </p>
          <div className="flex gap-4 flex-wrap">
            {LIGHTNING_WALLETS.map(wallet => (
              <a
                key={wallet.name}
                href={wallet.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`px-4 py-2 rounded-lg text-white font-semibold ${wallet.color} hover:opacity-90 transition`}
              >
                {wallet.name}
              </a>
            ))}
          </div>
        </div>

        {/* Save Bitcoin Card (supporting feature) */}
        <div className="bg-white dark:bg-[#232323] rounded-xl shadow-lg p-6 mt-8 w-full max-w-lg border border-gray-200 dark:border-bitcoin-glow flex flex-col items-center mb-8">
          <div className="text-lg font-semibold mb-2">Save as a Group or Individual</div>
          <a
            href={SAVE_SERVICES[0].url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-lg text-white font-bold bg-orange-700 hover:bg-orange-800 transition"
          >
            Save with Bitsacco
          </a>
        </div>
      </main>
    </div>
  );
};

export default Home; 