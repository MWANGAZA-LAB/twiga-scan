import React from 'react';

export interface ScanResultData {
  contentType: string;
  parsed: Record<string, any>;
  provider?: string;
  authStatus: 'Verified' | 'Suspicious' | 'Invalid';
  warnings?: string[];
}

interface ScanResultProps {
  result: ScanResultData | null;
  isDarkMode: boolean;
}

const ScanResult: React.FC<ScanResultProps> = ({ result, isDarkMode }) => {
  if (!result) return null;

  return (
    <div style={{
      border: `2px solid ${isDarkMode ? '#ff9900' : '#ff6600'}`,
      background: isDarkMode ? '#181818' : '#fff',
      color: isDarkMode ? '#fff' : '#333',
      padding: 20,
      borderRadius: 16,
      marginTop: 24,
      boxShadow: isDarkMode ? '0 4px 20px rgba(255, 153, 0, 0.2)' : '0 4px 20px rgba(0, 0, 0, 0.1)',
      maxWidth: '100%',
      overflow: 'hidden',
    }}>
      <h3 style={{ 
        color: isDarkMode ? '#ff9900' : '#ff6600', 
        marginBottom: 16,
        fontSize: 20,
        fontWeight: 600,
      }}>
        🔍 Scan Result
      </h3>
      <div style={{ marginBottom: 8 }}>
        <strong style={{ color: isDarkMode ? '#ff9900' : '#ff6600' }}>Type:</strong> 
        <span style={{ marginLeft: 8 }}>{result.contentType}</span>
      </div>
      <div style={{ marginBottom: 8 }}>
        <strong style={{ color: isDarkMode ? '#ff9900' : '#ff6600' }}>Provider:</strong> 
        <span style={{ marginLeft: 8 }}>{result.provider || 'Unknown'}</span>
      </div>
      <div style={{ marginBottom: 16 }}>
        <strong style={{ color: isDarkMode ? '#ff9900' : '#ff6600' }}>Status:</strong> 
        <span style={{ 
          marginLeft: 8,
          color: result.authStatus === 'Verified' ? '#21c96b' : result.authStatus === 'Suspicious' ? '#ff9900' : '#ff3b3b',
          fontWeight: 600,
        }}>
          {result.authStatus}
        </span>
      </div>
      <div style={{ marginTop: 16 }}>
        <strong style={{ color: isDarkMode ? '#ff9900' : '#ff6600', display: 'block', marginBottom: 8 }}>
          Parsed Fields:
        </strong>
        <div style={{
          background: isDarkMode ? '#232323' : '#f8f9fa',
          padding: 12,
          borderRadius: 8,
          maxHeight: 150,
          overflowX: 'auto',
          overflowY: 'auto',
          color: isDarkMode ? '#ffecb3' : '#495057',
          fontFamily: 'monospace',
          fontSize: 13,
          wordBreak: 'break-all',
          border: `1px solid ${isDarkMode ? '#444' : '#dee2e6'}`,
        }}>
          {JSON.stringify(result.parsed, null, 2)}
        </div>
      </div>
      {result.warnings && result.warnings.length > 0 && (
        <div style={{ 
          color: isDarkMode ? '#ff9900' : '#856404', 
          marginTop: 16,
          background: isDarkMode ? '#1a1a1a' : '#fff3cd',
          padding: 12,
          borderRadius: 8,
          border: `1px solid ${isDarkMode ? '#ff3b3b' : '#ffc107'}`,
        }}>
          <strong style={{ display: 'block', marginBottom: 8 }}>⚠️ Warnings:</strong>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ScanResult; 