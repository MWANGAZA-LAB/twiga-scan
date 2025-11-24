// Frontend Logger Utility
// Replaces console.log with environment-aware logging

const isDevelopment = process.env.NODE_ENV === 'development';

interface LoggerInterface {
  log: (...args: any[]) => void;
  error: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  info: (...args: any[]) => void;
  debug: (...args: any[]) => void;
}

class Logger implements LoggerInterface {
  log(...args: any[]): void {
    if (isDevelopment) {
      console.log('[LOG]', ...args);
    }
  }

  error(...args: any[]): void {
    if (isDevelopment) {
      console.error('[ERROR]', ...args);
    } else {
      // In production, send to error tracking service (Sentry, etc.)
      // TODO: Integrate with Sentry or similar service
      console.error('[ERROR]', ...args);
    }
  }

  warn(...args: any[]): void {
    if (isDevelopment) {
      console.warn('[WARN]', ...args);
    }
  }

  info(...args: any[]): void {
    if (isDevelopment) {
      console.info('[INFO]', ...args);
    }
  }

  debug(...args: any[]): void {
    if (isDevelopment) {
      console.debug('[DEBUG]', ...args);
    }
  }
}

export const logger = new Logger();
