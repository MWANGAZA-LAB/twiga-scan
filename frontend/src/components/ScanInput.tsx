import React, { useState, useRef } from 'react';
import CustomQrReader from './CustomQrReader';
import jsQR from 'jsqr';

interface ScanInputProps {
  onScan: (content: string) => void;
  isLoading?: boolean;
  isDarkMode?: boolean;
}

const ScanInput: React.FC<ScanInputProps> = ({ onScan, isLoading = false, isDarkMode = false }) => {
  const [inputValue, setInputValue] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onScan(inputValue.trim());
    }
  };

  const handleCameraResult = (result: any) => {
    if (result && result.text) {
      setShowCamera(false);
      onScan(result.text);
    }
  };

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
              onScan(code.data);
            } else {
              alert('No QR code found in the image');
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
    setShowCamera(!showCamera);
    setShowFileUpload(false);
  };

  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload);
    setShowCamera(false);
  };

  return (
    <div className="space-responsive-md">
      <h2 className="text-fluid-lg sm:text-xl lg:text-2xl font-semibold mb-3 sm:mb-4">
        Scan QR Code or Enter URL
      </h2>
      
      {/* Input Form - Responsive Layout */}
      <form onSubmit={handleSubmit} className="mb-4 sm:mb-6">
        {/* Desktop Layout */}
        <div className="hidden sm:flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter Bitcoin URI, Lightning invoice, or URL..."
            className={`flex-1 px-4 py-3 lg:py-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-base lg:text-lg font-mono transition-colors duration-200 touch-manipulation
              ${isDarkMode ? 'bg-gray-800 text-white placeholder-gray-400' : 'bg-white text-gray-900'}`}
            disabled={isLoading}
            aria-label="Payment identifier input"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className={`px-6 lg:px-8 py-3 lg:py-4 font-semibold rounded-lg transition-colors touch-target tap-transparent
              ${isDarkMode
                ? 'bg-orange-600 text-white hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-700'
                : 'bg-orange-600 text-white hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-400 disabled:cursor-not-allowed'}`}
            aria-label="Submit for verification"
          >
            {isLoading ? '🔍 Scanning...' : '🔍 Scan'}
          </button>
        </div>
        
        {/* Mobile Layout - Stacked */}
        <div className="flex sm:hidden flex-col gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter payment identifier..."
            className={`w-full px-4 py-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-base font-mono transition-colors duration-200 touch-target touch-manipulation
              ${isDarkMode ? 'bg-gray-800 text-white placeholder-gray-400' : 'bg-white text-gray-900'}`}
            disabled={isLoading}
            aria-label="Payment identifier input mobile"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className={`w-full px-6 py-4 font-semibold rounded-lg transition-colors touch-target-large tap-transparent
              ${isDarkMode
                ? 'bg-orange-600 text-white hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-700'
                : 'bg-orange-600 text-white hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-400 disabled:cursor-not-allowed'}`}
            aria-label="Submit for verification"
          >
            {isLoading ? '🔍 Scanning...' : '🔍 Scan'}
          </button>
        </div>
      </form>

      {/* Camera and File Upload Options - Responsive Grid */}
      <div className="grid grid-cols-1 xs:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <button
          onClick={toggleCamera}
          className={`w-full px-4 py-3 sm:py-4 font-semibold rounded-lg transition-colors touch-target-large tap-transparent flex items-center justify-center gap-2
            ${isDarkMode
              ? 'bg-blue-700 text-white hover:bg-blue-800 active:bg-blue-900'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'}`}
          aria-label={showCamera ? 'Close camera scanner' : 'Open camera scanner'}
        >
          <span className="text-xl sm:text-2xl">📷</span>
          <span className="text-fluid-sm sm:text-base">
            {showCamera ? 'Close Camera' : 'Open Camera'}
          </span>
        </button>
        <button
          onClick={toggleFileUpload}
          className={`w-full px-4 py-3 sm:py-4 font-semibold rounded-lg transition-colors touch-target-large tap-transparent flex items-center justify-center gap-2
            ${isDarkMode
              ? 'bg-green-700 text-white hover:bg-green-800 active:bg-green-900'
              : 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800'}`}
          aria-label={showFileUpload ? 'Close upload dialog' : 'Upload QR image'}
        >
          <span className="text-xl sm:text-2xl">📁</span>
          <span className="text-fluid-sm sm:text-base">
            {showFileUpload ? 'Close Upload' : 'Upload QR Image'}
          </span>
        </button>
      </div>

      {/* Camera - Responsive */}
      {showCamera && (
        <div className="mb-4 sm:mb-6 animate-fadeIn">
          <div className="border-2 border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden aspect-square sm:aspect-video max-h-[70vh]">
            <CustomQrReader
              onResult={handleCameraResult}
              onError={(err) => {
                if (process.env.NODE_ENV === 'development') {
                  console.error('Camera error:', err);
                }
              }}
              className="w-full h-full object-cover"
            />
          </div>
          <p className="text-fluid-sm sm:text-sm text-gray-600 dark:text-gray-300 mt-3 text-center">
            Point your camera at a QR code
          </p>
          {/* Close button for mobile */}
          <button
            onClick={toggleCamera}
            className="mt-3 w-full sm:hidden px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 active:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 touch-target tap-transparent"
            aria-label="Close camera"
          >
            ✕ Close Camera
          </button>
        </div>
      )}

      {/* File Upload - Responsive */}
      {showFileUpload && (
        <div className="mb-4 sm:mb-6 animate-fadeIn">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
            aria-label="QR code image file input"
          />
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 sm:p-8 lg:p-10 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
            <div className="flex flex-col items-center gap-4">
              <span className="text-4xl sm:text-5xl lg:text-6xl" role="img" aria-label="upload icon">
                📁
              </span>
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`px-6 sm:px-8 py-3 sm:py-4 font-semibold rounded-lg transition-colors touch-target-large tap-transparent
                  ${isDarkMode
                    ? 'bg-green-700 text-white hover:bg-green-800 active:bg-green-900'
                    : 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800'}`}
                aria-label="Select QR code image file"
              >
                📁 Select QR Code Image
              </button>
              <p className="text-fluid-sm sm:text-sm text-gray-600 dark:text-gray-300 mt-2">
                Upload an image containing a QR code
                <br />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Supports: JPG, PNG, WEBP
                </span>
              </p>
            </div>
          </div>
          {/* Close button for mobile */}
          <button
            onClick={toggleFileUpload}
            className="mt-3 w-full sm:hidden px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 active:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 touch-target tap-transparent"
            aria-label="Close upload dialog"
          >
            ✕ Close Upload
          </button>
        </div>
      )}
    </div>
  );
};

export default ScanInput; 