/**
 * 日志工具
 * 提供统一的日志输出，支持不同环境配置不同的日志级别
 */

// 日志级别
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// 当前日志级别（可根据环境配置）
const getLogLevel = (): LogLevel => {
  // 开发环境使用 debug，生产环境使用 info
  if (process.env.NODE_ENV === 'production') {
    return 'info';
  }
  return process.env.NEXT_PUBLIC_LOG_LEVEL as LogLevel || 'debug';
};

// 日志级别映射
const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const currentLevel = getLogLevel();

// 格式化日志消息
const formatMessage = (level: LogLevel, message: string, ...args: unknown[]): string => {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
  return args.length > 0
    ? `${prefix} ${message} ${args.map(arg => String(arg)).join(' ')}`
    : `${prefix} ${message}`;
};

// 输出日志
const log = (level: LogLevel, message: string, ...args: unknown[]): void => {
  if (LOG_LEVELS[level] >= LOG_LEVELS[currentLevel]) {
    const formattedMessage = formatMessage(level, message, ...args);
    switch (level) {
      case 'debug':
        // eslint-disable-next-line no-console
        console.debug(formattedMessage);
        break;
      case 'info':
        // eslint-disable-next-line no-console
        console.log(formattedMessage);
        break;
      case 'warn':
        // eslint-disable-next-line no-console
        console.warn(formattedMessage);
        break;
      case 'error':
        // eslint-disable-next-line no-console
        console.error(formattedMessage);
        break;
    }
  }
};

// 日志工具导出
export const logger = {
  debug: (message: string, ...args: unknown[]): void => log('debug', message, ...args),
  info: (message: string, ...args: unknown[]): void => log('info', message, ...args),
  warn: (message: string, ...args: unknown[]): void => log('warn', message, ...args),
  error: (message: string, ...args: unknown[]): void => log('error', message, ...args),
};

// 便捷方法
export const logDebug = (message: string, ...args: unknown[]): void => logger.debug(message, ...args);
export const logInfo = (message: string, ...args: unknown[]): void => logger.info(message, ...args);
export const logWarn = (message: string, ...args: unknown[]): void => logger.warn(message, ...args);
export const logError = (message: string, ...args: unknown[]): void => logger.error(message, ...args);
