import React, { useState, useEffect, useRef } from 'react';
import { apiService, ScanResponse } from '../services/api';
import Webcam from 'react-webcam';
import { BrowserQRCodeReader } from '@zxing/library';
import jsQR from 'jsqr';

const Home: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bitcoinPrice, setBitcoinPrice] = useState<number | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const webcamRef = useRef<Webcam>(null);
  const [isScanning, setIsScanning] = useState(false);

  // QR scanning with webcam
  const scanQRCode = React.useCallback(async () => {
    if (webcamRef.current && !isScanning) {
      setIsScanning(true);
      try {
        const screenshot = webcamRef.current.getScreenshot();
        if (screenshot) {
          const codeReader = new BrowserQRCodeReader();
          const result = await codeReader.decodeFromImageUrl(screenshot);
          if (result) {
            handleCameraResult({ text: result.getText() });
          }
        }
      } catch (error) {
        console.log('QR scan error:', error);
      } finally {
        setIsScanning(false);
      }
    }
  }, [isScanning]);

  // Auto-scan every 500ms when camera is active
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (showCamera) {
      interval = setInterval(scanQRCode, 500);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [showCamera, scanQRCode]);

  useEffect(() => {
    fetchBitcoinPrice();
    const interval = setInterval(fetchBitcoinPrice, 60000); // update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchBitcoinPrice = async () => {
    try {
      const response = await fetch(
        'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
      );
      const data = await response.json();
      setBitcoinPrice(data.bitcoin.usd);
    } catch (error) {
      // fail silently
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    setScanResult(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    setIsLoading(true);
    setError(null);
    setScanResult(null);
    try {
      const deviceId = `web-${navigator.userAgent.slice(0, 50)}`;
      const result = await apiService.scanContent({
        content: inputValue.trim(),
        device_id: deviceId,
        ip_address: '127.0.0.1',
      });
      setScanResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan content');
    } finally {
      setIsLoading(false);
    }
  };

  // Camera QR scan result
  const handleCameraResult = (result: { text?: string } | null) => {
    if (result?.text) {
      setShowCamera(false);
      setShowFileUpload(false);
      setInputValue(result.text);
      setScanResult(null);
      setTimeout(() => {
        document.getElementById('main-input')?.focus();
      }, 100);
    }
  };

  // File upload QR scan
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          if (ctx) {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            if (code) {
              setShowCamera(false);
              setShowFileUpload(false);
              setInputValue(code.data);
              setScanResult(null);
              setTimeout(() => {
                document.getElementById('main-input')?.focus();
              }, 100);
            } else {
              setError('No QR code found in the image');
            }
          }
        };
        img.src = event.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
    setShowFileUpload(false);
  };

  const toggleCamera = () => {
    setShowCamera((prev) => !prev);
    setShowFileUpload(false);
    setError(null);
  };

  const toggleFileUpload = () => {
    setShowFileUpload((prev) => !prev);
    setShowCamera(false);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#333]">
      <div className="w-full flex flex-col items-center">
        {/* Logo and Title */}
        <div className="flex flex-col items-center mb-2">
          <span className="text-7xl md:text-8xl mb-2 select-none" title="Twiga Logo">🦒</span>
          <h1 className="text-4xl md:text-5xl font-mono font-bold text-white mb-1 text-center">
            Twiga Scan<sup className="text-lg align-super ml-1">™</sup>
          </h1>
        </div>
        {/* Subtitle and Bitcoin Price */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 mb-2">
          <span className="text-lg md:text-xl font-mono text-gray-300 text-center">
            Bitcoin/Lightning QR & URL Authentication Platform
          </span>
          {bitcoinPrice !== null && (
            <span className="text-lg font-mono text-green-400 bg-black px-4 py-1 rounded-full border border-green-700 ml-0 md:ml-4 mt-2 md:mt-0">
              ₿ {bitcoinPrice.toLocaleString()} USD
            </span>
          )}
        </div>
        {/* Catch phrase */}
        <div className="text-md md:text-lg font-mono text-gray-400 mb-10 text-center italic">"Scan smarter, send safer."</div>
        {/* Input Row */}
        <form onSubmit={handleSubmit} className="w-full max-w-xl flex items-center justify-center">
          <div className="flex w-full">
            <span className="flex items-center px-4 bg-black text-gray-400 text-2xl rounded-l-lg border-r border-gray-700">⚡</span>
            <input
              id="main-input"
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Enter Invoice"
              className="flex-1 px-4 py-4 bg-black text-white text-2xl font-mono rounded-none focus:outline-none border-none placeholder-gray-500"
              disabled={isLoading}
              style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-4 bg-black text-white text-2xl rounded-none border-l border-gray-700 hover:bg-gray-800 focus:outline-none disabled:opacity-50"
              style={{ borderTopRightRadius: '0.5rem', borderBottomRightRadius: '0.5rem' }}
              title="Decode"
            >
              ➔
            </button>
            <button
              type="button"
              onClick={toggleCamera}
              className="ml-2 px-4 py-4 bg-black text-white text-2xl rounded-full border border-gray-700 hover:bg-gray-800 focus:outline-none"
              title="Scan QR Code with Camera"
            >
              <span role="img" aria-label="qr">📷</span>
            </button>
            <button
              type="button"
              onClick={toggleFileUpload}
              className="ml-2 px-4 py-4 bg-black text-white text-2xl rounded-full border border-gray-700 hover:bg-gray-800 focus:outline-none"
              title="Upload QR Code Image"
            >
              <span role="img" aria-label="upload">📁</span>
            </button>
          </div>
        </form>
        {/* Inline Camera/File Upload Section */}
        {(showCamera || showFileUpload) && (
          <div className="w-full max-w-xl mt-6 flex flex-col items-center">
            {showCamera && (
              <div className="w-full flex flex-col items-center mb-4">
                <div className="w-full border-2 border-gray-700 rounded-lg overflow-hidden bg-black">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    className="w-full"
                    videoConstraints={{
                      facingMode: 'environment'
                    }}
                  />
                </div>
                <p className="text-sm text-gray-400 mt-2 text-center">
                  Point your camera at a QR code
                  {isScanning && " (Scanning...)"}
                </p>
              </div>
            )}
            {showFileUpload && (
              <div className="w-full flex flex-col items-center mb-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center bg-black w-full">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-6 py-3 font-semibold rounded-lg transition-colors bg-green-700 text-white hover:bg-green-800"
                  >
                    📁 Select QR Code Image
                  </button>
                  <p className="text-sm text-gray-400 mt-2">Upload an image containing a QR code</p>
                </div>
              </div>
            )}
          </div>
        )}
        {/* Minimalist Scan Result */}
        {scanResult && (
          <div className="mt-8 flex flex-col items-center">
            {scanResult.auth_status === 'Verified' ? (
              <div className="flex items-center text-green-400 text-2xl font-mono font-bold gap-2">
                <span>✅ Valid</span>
              </div>
            ) : (
              <div className="flex items-center text-red-400 text-2xl font-mono font-bold gap-2">
                <span>❌ Invalid</span>
              </div>
            )}
          </div>
        )}
        {error && (
          <div className="mt-6 text-red-400 font-mono text-lg text-center">{error}</div>
        )}
      </div>
    </div>
  );
};

export default Home; 