import DOMPurify from 'dompurify';

// Install DOMPurify dependency
<dyad-add-dependency packages="dompurify"></dyad-add-dependency>

/**
 * Sanitize HTML content to prevent XSS attacks
 */
export const sanitizeHTML = (dirty: string): string => {
  if (typeof window !== 'undefined') {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
      FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed'],
      FORBID_ATTR: ['onclick', 'onload', 'onerror', 'style'],
    });
  }
  return dirty; // Fallback for server-side rendering
};

/**
 * Encode HTML entities to prevent XSS
 */
export const encodeHTML = (str: string): string => {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validate and sanitize URL to prevent javascript: and other dangerous protocols
 */
export const sanitizeURL = (url: string): string => {
  try {
    const parsed = new URL(url, window.location.origin);
    const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:', 'ftp:'];
    
    if (!allowedProtocols.includes(parsed.protocol)) {
      return 'about:blank';
    }
    
    return parsed.toString();
  } catch {
    return 'about:blank';
  }
};

/**
 * Safe way to set innerHTML with sanitization
 */
export const setSafeHTML = (element: HTMLElement, html: string): void => {
  element.innerHTML = sanitizeHTML(html);
};

/**
 * Validate and sanitize user input for display
 */
export const sanitizeUserInput = (input: string): string => {
  if (typeof input !== 'string') return '';
  
  // First encode to prevent XSS, then sanitize to allow safe HTML
  const encoded = encodeHTML(input);
  return sanitizeHTML(encoded);
};

/**
 * Strip potentially dangerous characters from input
 */
export const stripDangerousChars = (input: string): string => {
  return input.replace(/[<>"'`]/g, '');
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 254;
};

/**
 * Validate and sanitize file name
 */
export const sanitizeFileName = (fileName: string): string => {
  return fileName.replace(/[^a-zA-Z0-9.\-_]/g, '_').substring(0, 255);
};