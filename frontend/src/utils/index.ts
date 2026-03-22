import { ElMessage } from 'element-plus';
import toClipboard from './copy-to-memory';

/**
 * 复制文本到剪贴板
 * @param text 要复制的文本
 * @returns Promise
 */
export const copyText = async (text: string): Promise<void> => {
  try {
    await toClipboard(text);
    ElMessage.success('复制成功');
  } catch (error) {
    ElMessage.error('复制失败');
    throw error;
  }
};

/**
 * 验证并处理空格
 * @param val 输入值
 * @returns 处理后的值
 */
export const verifyAndSpace = (val: string): string => {
  return val.replace(/\s/g, '');
};

/**
 * 判断是否为移动端
 * @returns boolean
 */
export const isMobile = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

/**
 * 获取浏览器信息
 * @returns 浏览器信息对象
 */
export const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  const isChrome = /Chrome/.test(ua) && /Google Inc/.test(navigator.vendor);
  const isFirefox = /Firefox/.test(ua);
  const isSafari = /Safari/.test(ua) && /Apple Computer/.test(navigator.vendor);
  const isEdge = /Edge/.test(ua);
  
  return {
    isChrome,
    isFirefox,
    isSafari,
    isEdge,
    userAgent: ua
  };
};

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param wait 等待时间
 * @returns 防抖后的函数
 */
export const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * 节流函数
 * @param func 要节流的函数
 * @param limit 限制时间
 * @returns 节流后的函数
 */
export const throttle = (func: Function, limit: number) => {
  let inThrottle: boolean;
  return function executedFunction(...args: any[]) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};