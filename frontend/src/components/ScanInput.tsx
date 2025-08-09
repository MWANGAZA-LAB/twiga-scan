import React, { useState, useRef } from 'react';
import { QrReader } from '@uides/react-qr-reader';
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
    <div>
      <h2 className="text-xl font-semibold mb-4">Scan QR Code or Enter URL</h2>
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter Bitcoin URI, Lightning invoice, or URL..."
            className={`flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-lg font-mono transition-colors duration-200
              ${isDarkMode ? 'bg-gray-800 text-white placeholder-gray-400' : 'bg-white text-gray-900'}`}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className={`px-6 py-3 font-semibold rounded-lg transition-colors
              ${isDarkMode
                ? 'bg-orange-600 text-white hover:bg-orange-700 disabled:bg-gray-700'
                : 'bg-orange-600 text-white hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed'}`}
          >
            {isLoading ? '🔍 Scanning...' : '🔍 Scan'}
          </button>
        </div>
      </form>

      {/* Camera and File Upload Options */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={toggleCamera}
          className={`flex-1 px-4 py-3 font-semibold rounded-lg transition-colors
            ${isDarkMode
              ? 'bg-blue-700 text-white hover:bg-blue-800'
              : 'bg-blue-600 text-white hover:bg-blue-700'}`}
        >
          📷 {showCamera ? 'Close Camera' : 'Open Camera'}
        </button>
        <button
          onClick={toggleFileUpload}
          className={`flex-1 px-4 py-3 font-semibold rounded-lg transition-colors
            ${isDarkMode
              ? 'bg-green-700 text-white hover:bg-green-800'
              : 'bg-green-600 text-white hover:bg-green-700'}`}
        >
          📁 {showFileUpload ? 'Close Upload' : 'Upload QR Image'}
        </button>
      </div>

      {/* Camera */}
      {showCamera && (
        <div className="mb-6">
          <div className="border-2 border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <QrReader
              onResult={handleCameraResult}
              constraints={{ facingMode: 'environment' }}
              className="w-full"
            />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 text-center">
            Point your camera at a QR code
          </p>
        </div>
      )}

      {/* File Upload */}
      {showFileUpload && (
        <div className="mb-6">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
            <button
              onClick={() => fileInputRef.current?.click()}
              className={`px-6 py-3 font-semibold rounded-lg transition-colors
                ${isDarkMode
                  ? 'bg-green-700 text-white hover:bg-green-800'
                  : 'bg-green-600 text-white hover:bg-green-700'}`}
            >
              📁 Select QR Code Image
            </button>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
              Upload an image containing a QR code
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanInput; 