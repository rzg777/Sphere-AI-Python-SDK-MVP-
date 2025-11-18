import { useCallback } from 'react';
import { sanitizeInput, sanitizeURL } from '@/utils/security';

/**
 * Custom hook for security-related functionality in React components
 */
export const useSecurity = () => {
  const safeInput = useCallback((input: string): string => {
    return sanitizeInput(input);
  }, []);

  const safeURL = useCallback((url: string): string => {
    return sanitizeURL(url);
  }, []);

  const validateEmail = useCallback((email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) && email.length <= 254;
  }, []);

  const validatePassword = useCallback((password: string): { isValid: boolean; issues: string[] } => {
    const issues: string[] = [];
    
    if (password.length < 8) {
      issues.push('Password must be at least 8 characters long');
    }
    if (!/(?=.*[a-z])/.test(password)) {
      issues.push('Password must contain at least one lowercase letter');
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      issues.push('Password must contain at least one uppercase letter');
    }
    if (!/(?=.*\d)/.test(password)) {
      issues.push('Password must contain at least one number');
    }
    if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(password)) {
      issues.push('Password must contain at least one special character');
    }

    return {
      isValid: issues.length === 0,
      issues
    };
  }, []);

  return {
    safeInput,
    safeURL,
    validateEmail,
    validatePassword
  };
};