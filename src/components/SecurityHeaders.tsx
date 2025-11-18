"use client";

import { useEffect } from 'react';

/**
 * SecurityHeaders component that adds additional security measures
 * This works alongside the CSP meta tags for comprehensive protection
 */
const SecurityHeaders: React.FC = () => {
  useEffect(() => {
    // Additional client-side security measures
    const handlePotentialXSS = () => {
      // Sanitize any user inputs that might be rendered
      // This is a basic example - in production, use a proper sanitization library
      const sanitizeInput = (input: string): string => {
        return input
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#x27;')
          .replace(/\//g, '&#x2F;');
      };

      // Store the original innerHTML setter to monitor for potential XSS
      const originalSetInnerHTML = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML')?.set;
      
      if (originalSetInnerHTML) {
        Object.defineProperty(Element.prototype, 'innerHTML', {
          set: function(value) {
            // Basic check for script tags - in production use a proper sanitizer
            if (typeof value === 'string' && value.toLowerCase().includes('<script')) {
              console.warn('Potential XSS attempt detected and blocked');
              return;
            }
            originalSetInnerHTML.call(this, value);
          }
        });
      }
    };

    handlePotentialXSS();
  }, []);

  return null; // This component doesn't render anything
};

export default SecurityHeaders;