import React, { useEffect, useRef, useState } from 'react';
import { BrowserMultiFormatReader, Result } from '@zxing/library';

interface CustomQrReaderProps {
  onResult: (result: any) => void;
  onError?: (error: any) => void;
  className?: string;
  style?: React.CSSProperties;
}

const CustomQrReader: React.FC<CustomQrReaderProps> = ({ 
  onResult, 
  onError, 
  className = '', 
  style = {} 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    const codeReader = new BrowserMultiFormatReader();
    codeReaderRef.current = codeReader;

    const startScanning = async () => {
      try {
        setIsScanning(true);
        setError(null);
        
        // Use the correct API signature for ZXing library
        await codeReader.decodeFromVideoDevice(
          null,
          videoRef.current!,
          (result: Result | null, error: any) => {
            if (result) {
              onResult({ text: result.getText() });
            }
            if (error && error.name !== 'NotFoundException') {
              setError(error.message);
              onError?.(error);
            }
          }
        );
      } catch (err: any) {
        setError(err.message);
        onError?.(err);
      }
    };

    startScanning();

    return () => {
      if (codeReaderRef.current) {
        codeReaderRef.current.reset();
      }
    };
  }, [onResult, onError]);

  const handleStopScanning = () => {
    if (codeReaderRef.current) {
      codeReaderRef.current.reset();
      setIsScanning(false);
    }
  };

  return (
    <div className={className} style={style}>
      <video
        ref={videoRef}
        style={{ width: '100%', height: 'auto' }}
        autoPlay
        playsInline
        muted
      />
      {error && (
        <div className="text-red-500 text-sm mt-2 text-center">
          Camera error: {error}
        </div>
      )}
      {isScanning && (
        <button
          onClick={handleStopScanning}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Stop Camera
        </button>
      )}
    </div>
  );
};

export default CustomQrReader;
