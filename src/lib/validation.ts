import { z } from 'zod';

// Common validation patterns
export const emailSchema = z.string().email('Please enter a valid email address');
export const passwordSchema = z.string().min(8, 'Password must be at least 8 characters')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^a-zA-Z0-9]/, 'Password must contain at least one special character');

export const nameSchema = z.string()
  .min(2, 'Name must be at least 2 characters')
  .max(50, 'Name must be less than 50 characters')
  .regex(/^[a-zA-Z\s\-']+$/, 'Name can only contain letters, spaces, hyphens, and apostrophes');

export const urlSchema = z.string().url('Please enter a valid URL').optional().or(z.literal(''));

// Login form validation
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

// User registration validation
export const registerSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// Profile update validation
export const profileSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  avatar: urlSchema,
});

// Generic text input validation (for comments, messages, etc.)
export const textInputSchema = z.object({
  content: z.string()
    .min(1, 'Content cannot be empty')
    .max(10000, 'Content must be less than 10000 characters')
    .refine((val) => {
      // Basic XSS prevention - check for common attack patterns
      const dangerousPatterns = [
        /&lt;script/i,
        /javascript:/i,
        /onload=/i,
        /onerror=/i,
        /onclick=/i,
        /vbscript:/i,
      ];
      return !dangerousPatterns.some(pattern => pattern.test(val));
    }, 'Content contains potentially dangerous patterns'),
});

// Search input validation
export const searchSchema = z.object({
  query: z.string()
    .max(200, 'Search query too long')
    .refine((val) => {
      // Prevent SQL injection patterns in search
      const sqlPatterns = [
        /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC)\b)/i,
        /('|"|;|--)/,
      ];
      return !sqlPatterns.some(pattern => pattern.test(val));
    }, 'Invalid search query'),
});

// Numeric input validation
export const numberSchema = z.number()
  .min(0, 'Number must be positive')
  .max(999999, 'Number too large');

// File upload validation
export const fileSchema = z.object({
  file: z.instanceof(File).optional(),
  fileName: z.string().max(255, 'File name too long').optional(),
}).refine((data) => {
  if (data.file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    return validTypes.includes(data.file.type) && data.file.size <= maxSize;
  }
  return true;
}, {
  message: 'File must be JPEG, PNG, GIF, or PDF and less than 10MB',
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ProfileFormData = z.infer<typeof profileSchema>;
export type TextInputData = z.infer<typeof textInputSchema>;
export type SearchData = z.infer<typeof searchSchema>;