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
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#333] safe-top safe-bottom px-4 sm:px-6 lg:px-8">
      <div className="w-full flex flex-col items-center container-responsive max-w-7xl">
        {/* Logo and Title - Responsive Sizing */}
        <div className="flex flex-col items-center mb-4 sm:mb-6 lg:mb-8">
          <span 
            className="text-6xl xs:text-7xl sm:text-8xl lg:text-9xl mb-2 sm:mb-3 select-none transition-transform hover:scale-110 duration-300" 
            title="Twiga Logo"
            role="img"
            aria-label="Giraffe emoji representing Twiga brand"
          >
            🦒
          </span>
          <h1 className="text-fluid-xl sm:text-5xl lg:text-6xl xl:text-7xl font-mono font-bold text-white mb-2 text-center px-2">
            Twiga Scan<sup className="text-sm sm:text-base lg:text-lg align-super ml-1">™</sup>
          </h1>
        </div>
        
        {/* Subtitle and Bitcoin Price - Stacked on Mobile, Inline on Tablet+ */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 lg:gap-6 mb-3 sm:mb-4 w-full max-w-4xl">
          <span className="text-fluid-sm sm:text-base lg:text-lg font-mono text-gray-300 text-center px-4 leading-relaxed">
            Bitcoin/Lightning QR & URL Authentication Platform
          </span>
          {bitcoinPrice !== null && (
            <span className="text-fluid-sm sm:text-base lg:text-lg font-mono text-green-400 bg-black px-4 py-2 rounded-full border border-green-700 whitespace-nowrap touch-target shadow-touch">
              ₿ {bitcoinPrice.toLocaleString()} USD
            </span>
          )}
        </div>
        
        {/* Catch phrase */}
        <div className="text-fluid-sm sm:text-base lg:text-lg font-mono text-gray-400 mb-6 sm:mb-8 lg:mb-10 text-center italic px-4">
          "Scan smarter, send safer."
        </div>
        
        {/* Input Row - Responsive Layout */}
        <form 
          onSubmit={handleSubmit} 
          className="w-full max-w-xl lg:max-w-3xl xl:max-w-4xl flex items-center justify-center px-2 sm:px-4"
        >
          {/* Desktop Layout (md+) */}
          <div className="hidden md:flex w-full">
            <span className="flex items-center px-3 lg:px-4 bg-black text-gray-400 text-xl lg:text-2xl rounded-l-lg border-r border-gray-700 touch-target">
              ⚡
            </span>
            <input
              id="main-input"
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Enter Invoice, Address, or URL"
              className="flex-1 px-3 lg:px-4 py-3 lg:py-4 bg-black text-white text-lg lg:text-2xl font-mono rounded-none focus:outline-none focus:ring-2 focus:ring-orange-500 border-none placeholder-gray-500 touch-manipulation"
              disabled={isLoading}
              aria-label="Payment identifier input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-4 lg:px-6 py-3 lg:py-4 bg-black text-white text-xl lg:text-2xl rounded-none border-l border-gray-700 hover:bg-gray-800 active:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed touch-target transition-colors tap-transparent"
              style={{ borderTopRightRadius: '0.5rem', borderBottomRightRadius: '0.5rem' }}
              title="Decode and verify"
              aria-label="Submit for verification"
            >
              ➔
            </button>
            <button
              type="button"
              onClick={toggleCamera}
              className="ml-2 lg:ml-3 px-3 lg:px-4 py-3 lg:py-4 bg-black text-white text-xl lg:text-2xl rounded-full border border-gray-700 hover:bg-gray-800 active:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 touch-target-comfortable transition-all tap-transparent shadow-touch hover:shadow-touch-active"
              title="Scan QR Code with Camera"
              aria-label="Open camera scanner"
            >
              <span role="img" aria-label="camera">📷</span>
            </button>
            <button
              type="button"
              onClick={toggleFileUpload}
              className="ml-2 lg:ml-3 px-3 lg:px-4 py-3 lg:py-4 bg-black text-white text-xl lg:text-2xl rounded-full border border-gray-700 hover:bg-gray-800 active:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 touch-target-comfortable transition-all tap-transparent shadow-touch hover:shadow-touch-active"
              title="Upload QR Code Image"
              aria-label="Upload QR code image"
            >
              <span role="img" aria-label="upload">📁</span>
            </button>
          </div>
          
          {/* Mobile/Tablet Layout (< md) - Stacked for Better Touch Targets */}
          <div className="flex md:hidden flex-col w-full gap-3">
            {/* Input with icon */}
            <div className="flex w-full">
              <span className="flex items-center px-3 xs:px-4 bg-black text-gray-400 text-xl xs:text-2xl rounded-l-lg border-r border-gray-700 touch-target">
                ⚡
              </span>
              <input
                id="main-input-mobile"
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                placeholder="Enter Invoice"
                className="flex-1 px-3 xs:px-4 py-4 bg-black text-white text-base xs:text-lg font-mono rounded-r-lg focus:outline-none focus:ring-2 focus:ring-orange-500 border-none placeholder-gray-500 touch-manipulation touch-target"
                disabled={isLoading}
                aria-label="Payment identifier input mobile"
              />
            </div>
            
            {/* Action buttons - Full width on mobile */}
            <div className="grid grid-cols-3 gap-2 w-full">
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="col-span-1 px-3 py-3 bg-orange-600 text-white text-sm xs:text-base font-semibold rounded-lg hover:bg-orange-700 active:bg-orange-800 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 disabled:bg-gray-600 touch-target-large transition-colors tap-transparent shadow-touch"
                title="Verify"
                aria-label="Submit for verification"
              >
                {isLoading ? '⏳' : '✓ Verify'}
              </button>
              <button
                type="button"
                onClick={toggleCamera}
                className="col-span-1 px-3 py-3 bg-blue-600 text-white text-sm xs:text-base font-semibold rounded-lg hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 touch-target-large transition-all tap-transparent shadow-touch"
                title="Camera"
                aria-label="Open camera scanner"
              >
                📷 Scan
              </button>
              <button
                type="button"
                onClick={toggleFileUpload}
                className="col-span-1 px-3 py-3 bg-green-600 text-white text-sm xs:text-base font-semibold rounded-lg hover:bg-green-700 active:bg-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 touch-target-large transition-all tap-transparent shadow-touch"
                title="Upload"
                aria-label="Upload QR code image"
              >
                📁 Upload
              </button>
            </div>
          </div>
        </form>
        {/* Inline Camera/File Upload Section - Responsive */}
        {(showCamera || showFileUpload) && (
          <div className="w-full max-w-xl lg:max-w-3xl mt-4 sm:mt-6 lg:mt-8 flex flex-col items-center px-2 sm:px-4">
            {showCamera && (
              <div className="w-full flex flex-col items-center mb-4 animate-fadeIn">
                <div className="w-full border-2 border-gray-700 rounded-lg overflow-hidden bg-black shadow-bitcoin aspect-square sm:aspect-video max-h-[70vh]">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    className="w-full h-full object-cover"
                    videoConstraints={{
                      facingMode: 'environment',
                      aspectRatio: { ideal: 1 },
                      width: { ideal: 1280 },
                      height: { ideal: 1280 },
                    }}
                    aria-label="QR code camera scanner"
                  />
                </div>
                <div className="flex items-center gap-2 mt-3 sm:mt-4">
                  <p className="text-fluid-sm sm:text-base text-gray-400 text-center">
                    {isScanning ? (
                      <>
                        <span className="inline-block animate-pulse">🔍</span> Scanning...
                      </>
                    ) : (
                      'Point your camera at a QR code'
                    )}
                  </p>
                </div>
                {/* Close button for mobile */}
                <button
                  onClick={toggleCamera}
                  className="mt-4 px-6 py-3 bg-red-600 text-white text-sm sm:text-base font-semibold rounded-lg hover:bg-red-700 active:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 touch-target transition-colors tap-transparent shadow-touch md:hidden"
                  aria-label="Close camera"
                >
                  ✕ Close Camera
                </button>
              </div>
            )}
            {showFileUpload && (
              <div className="w-full flex flex-col items-center mb-4 animate-fadeIn">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  aria-label="QR code image upload input"
                />
                <div className="border-2 border-dashed border-gray-700 rounded-lg p-6 sm:p-8 lg:p-10 text-center bg-black w-full hover:border-gray-600 transition-colors">
                  <div className="flex flex-col items-center gap-4">
                    <span className="text-4xl sm:text-5xl lg:text-6xl" role="img" aria-label="upload icon">
                      📁
                    </span>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="px-6 sm:px-8 py-3 sm:py-4 font-semibold rounded-lg transition-colors bg-green-600 text-white hover:bg-green-700 active:bg-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 touch-target-large text-sm sm:text-base lg:text-lg tap-transparent shadow-touch"
                      aria-label="Select QR code image file"
                    >
                      📁 Select QR Code Image
                    </button>
                    <p className="text-fluid-sm sm:text-base text-gray-400 mt-2 px-4">
                      Upload an image containing a QR code
                      <br />
                      <span className="text-xs sm:text-sm text-gray-500">
                        Supports: JPG, PNG, WEBP
                      </span>
                    </p>
                  </div>
                </div>
                {/* Close button for mobile */}
                <button
                  onClick={toggleFileUpload}
                  className="mt-4 px-6 py-3 bg-red-600 text-white text-sm sm:text-base font-semibold rounded-lg hover:bg-red-700 active:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 touch-target transition-colors tap-transparent shadow-touch md:hidden"
                  aria-label="Close upload dialog"
                >
                  ✕ Close Upload
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* Minimalist Scan Result - Responsive */}
        {scanResult && (
          <div className="mt-6 sm:mt-8 lg:mt-10 flex flex-col items-center w-full max-w-md lg:max-w-lg px-4 animate-fadeIn">
            {scanResult.auth_status === 'Verified' ? (
              <div className="flex flex-col sm:flex-row items-center justify-center text-green-400 text-fluid-lg sm:text-2xl lg:text-3xl font-mono font-bold gap-2 sm:gap-3 bg-green-900/20 border-2 border-green-500 rounded-lg px-6 sm:px-8 py-4 sm:py-6 w-full shadow-bitcoin">
                <span className="text-3xl sm:text-4xl">✅</span>
                <span>Valid & Verified</span>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center justify-center text-red-400 text-fluid-lg sm:text-2xl lg:text-3xl font-mono font-bold gap-2 sm:gap-3 bg-red-900/20 border-2 border-red-500 rounded-lg px-6 sm:px-8 py-4 sm:py-6 w-full shadow-touch">
                <span className="text-3xl sm:text-4xl">❌</span>
                <span>Invalid</span>
              </div>
            )}
            
            {/* Duplicate Detection Warning - Responsive */}
            {scanResult.is_duplicate && (
              <div className="mt-4 w-full bg-yellow-900/20 border-2 border-yellow-500 rounded-lg px-4 sm:px-6 py-3 sm:py-4">
                <p className="text-yellow-400 text-fluid-sm sm:text-base font-mono text-center">
                  ⚠️ Address used {scanResult.usage_count} time(s)
                </p>
                {scanResult.warnings && scanResult.warnings.length > 0 && (
                  <div className="mt-2 text-yellow-300 text-xs sm:text-sm">
                    {scanResult.warnings.map((warning, index) => (
                      <p key={index} className="text-center">{warning}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* Error Display - Responsive */}
        {error && (
          <div className="mt-4 sm:mt-6 text-red-400 font-mono text-fluid-sm sm:text-base lg:text-lg text-center px-4 max-w-lg bg-red-900/20 border border-red-500 rounded-lg py-3 sm:py-4 animate-fadeIn">
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 