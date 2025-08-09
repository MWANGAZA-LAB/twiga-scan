declare module 'react-qr-reader' {
  import React from 'react';

  interface QrReaderProps {
    onResult: (result: any) => void;
    constraints?: MediaTrackConstraints;
    className?: string;
    style?: React.CSSProperties;
  }

  export const QrReader: React.FC<QrReaderProps>;
}
