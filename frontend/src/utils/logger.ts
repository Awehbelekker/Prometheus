/**
 * Centralized logging utility for Prometheus Frontend
 * 
 * Provides consistent logging with environment-aware behavior:
 * - Development: All logs enabled
 * - Production: Only errors and warnings
 * - Can be extended to send logs to monitoring service
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  data?: any;
  timestamp: string;
  context?: string;
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development';
  private isProduction = process.env.NODE_ENV === 'production';
  
  // In production, we might want to send logs to a monitoring service
  private logToService = false; // Set to true when monitoring service is configured

  private formatMessage(level: LogLevel, message: string, data?: any, context?: string): LogEntry {
    return {
      level,
      message,
      data,
      timestamp: new Date().toISOString(),
      context
    };
  }

  private shouldLog(level: LogLevel): boolean {
    if (this.isDevelopment) {
      return true; // Log everything in development
    }
    
    if (this.isProduction) {
      // In production, only log warnings and errors
      return level === 'warn' || level === 'error';
    }
    
    return true;
  }

  private log(level: LogLevel, message: string, data?: any, context?: string): void {
    if (!this.shouldLog(level)) {
      return;
    }

    const entry = this.formatMessage(level, message, data, context);
    
    // Console logging
    const consoleMethod = level === 'error' ? console.error :
                         level === 'warn' ? console.warn :
                         level === 'info' ? console.info :
                         console.log;
    
    if (data) {
      consoleMethod(`[${entry.timestamp}] [${level.toUpperCase()}]${context ? ` [${context}]` : ''} ${message}`, data);
    } else {
      consoleMethod(`[${entry.timestamp}] [${level.toUpperCase()}]${context ? ` [${context}]` : ''} ${message}`);
    }

    // Future: Send to monitoring service in production
    if (this.logToService && this.isProduction && (level === 'error' || level === 'warn')) {
      // TODO: Implement service integration (e.g., Sentry, LogRocket, etc.)
      // this.sendToMonitoringService(entry);
    }
  }

  /**
   * Debug logs - only in development
   */
  debug(message: string, data?: any, context?: string): void {
    this.log('debug', message, data, context);
  }

  /**
   * Info logs - development only, or important info in production
   */
  info(message: string, data?: any, context?: string): void {
    this.log('info', message, data, context);
  }

  /**
   * Warning logs - always logged
   */
  warn(message: string, data?: any, context?: string): void {
    this.log('warn', message, data, context);
  }

  /**
   * Error logs - always logged, should be used for actual errors
   */
  error(message: string, error?: Error | any, context?: string): void {
    const errorData = error instanceof Error 
      ? { message: error.message, stack: error.stack, name: error.name }
      : error;
    this.log('error', message, errorData, context);
  }

  /**
   * Group related logs together (development only)
   */
  group(label: string): void {
    if (this.isDevelopment) {
      console.group(label);
    }
  }

  groupEnd(): void {
    if (this.isDevelopment) {
      console.groupEnd();
    }
  }

  /**
   * Log API call (useful for debugging)
   */
  apiCall(method: string, endpoint: string, status?: number, duration?: number): void {
    if (this.isDevelopment) {
      const message = `${method} ${endpoint}${status ? ` → ${status}` : ''}${duration ? ` (${duration}ms)` : ''}`;
      this.debug(message, undefined, 'API');
    }
  }

  /**
   * Log component lifecycle events (development only)
   */
  componentLifecycle(component: string, event: 'mount' | 'update' | 'unmount', props?: any): void {
    if (this.isDevelopment) {
      this.debug(`Component ${event}: ${component}`, props, 'Component');
    }
  }

  /**
   * Log performance metrics
   */
  performance(metric: string, value: number, unit: string = 'ms'): void {
    if (this.isDevelopment) {
      this.info(`Performance: ${metric} = ${value}${unit}`, undefined, 'Performance');
    }
  }
}

// Export singleton instance
export const logger = new Logger();

// Export class for testing
export { Logger };

// Convenience exports for common use cases
export const logDebug = (message: string, data?: any, context?: string) => logger.debug(message, data, context);
export const logInfo = (message: string, data?: any, context?: string) => logger.info(message, data, context);
export const logWarn = (message: string, data?: any, context?: string) => logger.warn(message, data, context);
export const logError = (message: string, error?: Error | any, context?: string) => logger.error(message, error, context);

