/**
 * Security utilities for XSS protection and input sanitization
 */

/**
 * Basic HTML entity encoding to prevent XSS
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
 * Sanitize user input for safe display
 */
export const sanitizeInput = (input: string): string => {
  if (typeof input !== 'string') return '';
  
  return encodeHTML(input)
    .replace(/\b(javascript|vbscript|script|onload|onerror|onclick):/gi, '')
    .replace(/&amp;#/g, '&#'); // Allow numeric entities
};

/**
 * Validate URL to prevent javascript: and other dangerous protocols
 */
export const sanitizeURL = (url: string): string => {
  try {
    const parsed = new URL(url, window.location.origin);
    const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
    
    if (!allowedProtocols.includes(parsed.protocol)) {
      return 'about:blank';
    }
    
    return parsed.toString();
  } catch {
    return 'about:blank';
  }
};

/**
 * Safe way to set innerHTML with basic sanitization
 */
export const setSafeHTML = (element: HTMLElement, html: string): void => {
  element.innerHTML = sanitizeInput(html);
};