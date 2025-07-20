import React from 'react';
import { ScanResponse } from '../services/api';

interface ScanResultProps {
  result: ScanResponse;
}

const ScanResult: React.FC<ScanResultProps> = ({ result }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return 'text-green-600 bg-green-100 border-green-300';
      case 'suspicious':
        return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'invalid':
        return 'text-red-600 bg-red-100 border-red-300';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return '✅';
      case 'suspicious':
        return '⚠️';
      case 'invalid':
        return '❌';
      default:
        return '❓';
    }
  };

  const formatContentType = (type: string) => {
    switch (type) {
      case 'BIP21':
        return 'Bitcoin Payment URI (BIP21)';
      case 'BOLT11':
        return 'Lightning Invoice (BOLT11)';
      case 'LNURL':
        return 'Lightning Network URL (LNURL)';
      case 'LIGHTNING_ADDRESS':
        return 'Lightning Address';
      default:
        return type;
    }
  };

  const renderParsedData = (data: any, contentType: string) => {
    if (!data) return <p className="text-gray-500">No parsed data available</p>;

    switch (contentType) {
      case 'BIP21':
        return (
          <div className="space-y-2">
            <div><strong>Address:</strong> <code className="bg-gray-100 px-2 py-1 rounded">{data.address}</code></div>
            {data.amount && <div><strong>Amount:</strong> {data.amount} BTC</div>}
            {data.label && <div><strong>Label:</strong> {data.label}</div>}
            {data.message && <div><strong>Message:</strong> {data.message}</div>}
          </div>
        );
      
      case 'BOLT11':
        return (
          <div className="space-y-2">
            <div><strong>Invoice:</strong> <code className="bg-gray-100 dark:bg-gray-900 dark:text-white px-2 py-1 rounded text-xs break-all">{data.invoice}</code></div>
            {data.network && <div><strong>Network:</strong> <span className="dark:text-white">{data.network}</span></div>}
            {data.amount_sats && <div><strong>Amount:</strong> <span className="dark:text-white">{data.amount_sats} sats</span></div>}
          </div>
        );
      
      case 'LNURL':
        return (
          <div className="space-y-2">
            {data.url && <div><strong>URL:</strong> <code className="bg-gray-100 px-2 py-1 rounded break-all">{data.url}</code></div>}
            {data.domain && <div><strong>Domain:</strong> {data.domain}</div>}
            {data.type && <div><strong>Type:</strong> {data.type}</div>}
          </div>
        );
      
      case 'LIGHTNING_ADDRESS':
        return (
          <div className="space-y-2">
            <div><strong>Address:</strong> <code className="bg-gray-100 px-2 py-1 rounded">{data.lightning_address}</code></div>
            <div><strong>Username:</strong> {data.username}</div>
            <div><strong>Domain:</strong> {data.domain}</div>
          </div>
        );
      
      default:
        return (
          <div>
            <pre className="bg-gray-100 dark:bg-gray-900 dark:text-white p-3 rounded text-sm overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900">Scan Result</h3>
        <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(result.auth_status)}`}>
          {getStatusIcon(result.auth_status)} {result.auth_status}
        </div>
      </div>

      {/* Scan ID and Timestamp */}
      <div className="grid md:grid-cols-2 gap-4 mb-6 text-sm text-gray-600">
        <div>
          <strong>Scan ID:</strong> <code className="bg-gray-100 px-2 py-1 rounded">{result.scan_id}</code>
        </div>
        <div>
          <strong>Timestamp:</strong> {new Date(result.timestamp).toLocaleString()}
        </div>
      </div>

      {/* Content Type */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-2">Content Type</h4>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <span className="text-blue-800 font-medium">{formatContentType(result.content_type)}</span>
        </div>
      </div>

      {/* Parsed Data */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Parsed Data</h4>
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          {renderParsedData(result.parsed_data, result.content_type)}
        </div>
      </div>

      {/* Provider Information */}
      {result.provider && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">Provider</h4>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <span className="text-green-800">✅ Known Provider Identified</span>
          </div>
        </div>
      )}

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">Warnings</h4>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <ul className="list-disc list-inside space-y-1 text-yellow-800">
              {result.warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Verification Results */}
      {result.verification_results && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">Verification Details</h4>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Format Valid:</strong> {result.verification_results.format_valid ? '✅ Yes' : '❌ No'}
              </div>
              <div>
                <strong>Crypto Valid:</strong> {result.verification_results.crypto_valid ? '✅ Yes' : '❌ No'}
              </div>
              <div>
                <strong>Domain Valid:</strong> {result.verification_results.domain_valid ? '✅ Yes' : '❌ No'}
              </div>
              <div>
                <strong>Provider Known:</strong> {result.verification_results.provider_known ? '✅ Yes' : '❌ No'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Action */}
      {result.user_action && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">User Action</h4>
          <div className={`px-3 py-2 rounded-lg text-sm font-medium ${
            result.user_action === 'approved' 
              ? 'bg-green-100 text-green-800 border border-green-200'
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            {result.user_action === 'approved' ? '✅ Approved' : '❌ Aborted'}
          </div>
        </div>
      )}

      {/* Outcome */}
      {result.outcome && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">Outcome</h4>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <span className="text-gray-700">{result.outcome}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanResult; 