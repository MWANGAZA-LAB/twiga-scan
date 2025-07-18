import React, { useRef, useState } from 'react';
import { QrReader } from 'react-qr-reader';
import jsQR from 'jsqr';

interface ScanInputProps {
  onScan: (data: string) => void;
  isDarkMode: boolean;
}

const ScanInput: React.FC<ScanInputProps> = ({ onScan, isDarkMode }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showScanner, setShowScanner] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onScan(e.target.value);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    
    try {
      // Check if file is an image
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file (JPEG, PNG, etc.)');
        return;
      }

      // Create a canvas to process the image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Set canvas size to image size
        canvas.width = img.width;
        canvas.height = img.height;
        
        // Draw image on canvas
        ctx?.drawImage(img, 0, 0);
        
        // Get image data
        const imageData = ctx?.getImageData(0, 0, canvas.width, canvas.height);
        
        if (imageData) {
          // Decode QR code using jsQR
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          
          if (code) {
            // QR code found
            onScan(code.data);
            alert(`QR Code detected: ${code.data.substring(0, 50)}${code.data.length > 50 ? '...' : ''}`);
          } else {
            // No QR code found
            alert('No QR code found in the uploaded image. Please try a different image.');
          }
        } else {
          alert('Failed to process the image. Please try again.');
        }
        
        setIsProcessing(false);
        
        // Clear the file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      };

      img.onerror = () => {
        alert('Failed to load the image. Please try a different file.');
        setIsProcessing(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      };

      // Load the image
      const reader = new FileReader();
      reader.onload = (e) => {
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(file);

    } catch (error) {
      console.error('Error processing QR code:', error);
      alert('Error processing the image. Please try again.');
      setIsProcessing(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleScan = (result: any) => {
    if (result) {
      onScan(result?.text || '');
      setShowScanner(false);
    }
  };

  return (
    <div style={{ marginBottom: 24 }}>
      <label htmlFor="scan-text" style={{ color: isDarkMode ? '#fff' : '#333', display: 'block', marginBottom: 8 }}>
        Paste QR/URL string:
      </label>
      <input
        id="scan-text"
        type="text"
        onChange={handleTextChange}
        placeholder="Paste Bitcoin/Lightning URI, invoice, or LNURL"
        style={{
          width: '100%',
          padding: 12,
          marginBottom: 16,
          borderRadius: 8,
          border: `1px solid ${isDarkMode ? '#444' : '#ddd'}`,
          background: isDarkMode ? '#333' : '#fff',
          color: isDarkMode ? '#fff' : '#333',
          fontSize: 14,
        }}
      />
      <div style={{ marginBottom: 16 }}>
        <label htmlFor="scan-file" style={{ color: isDarkMode ? '#fff' : '#333', display: 'block', marginBottom: 8 }}>
          Or upload QR image:
        </label>
        <input
          id="scan-file"
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          disabled={isProcessing}
          style={{
            color: isDarkMode ? '#fff' : '#333',
            background: isDarkMode ? '#333' : '#fff',
            border: `1px solid ${isDarkMode ? '#444' : '#ddd'}`,
            borderRadius: 8,
            padding: 8,
            opacity: isProcessing ? 0.6 : 1,
          }}
        />
        {isProcessing && (
          <div style={{ 
            color: isDarkMode ? '#ff9900' : '#ff6600', 
            fontSize: 12, 
            marginTop: 4,
            fontStyle: 'italic'
          }}>
            🔍 Processing QR code...
          </div>
        )}
      </div>
      <button
        style={{
          background: '#ff9900',
          color: '#181818',
          border: 'none',
          padding: '10px 20px',
          borderRadius: 8,
          cursor: 'pointer',
          fontWeight: 600,
          fontSize: 14,
          marginBottom: 16,
        }}
        onClick={() => setShowScanner((s) => !s)}
      >
        {showScanner ? '📷 Close Camera Scanner' : '📷 Scan with Camera'}
      </button>
      {showScanner && (
        <div style={{
          marginTop: 16,
          maxWidth: 320,
          width: '100%',
          borderRadius: 12,
          overflow: 'hidden',
          border: `2px solid ${isDarkMode ? '#ff9900' : '#ff6600'}`,
        }}>
          <QrReader
            onResult={handleScan}
            constraints={{ facingMode: 'environment' }}
          />
        </div>
      )}
    </div>
  );
};

export default ScanInput; 