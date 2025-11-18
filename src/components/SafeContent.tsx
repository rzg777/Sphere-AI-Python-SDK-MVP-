"use client";

import React from 'react';
import { sanitizeHTML, encodeHTML } from '@/utils/sanitization';

interface SafeContentProps {
  content: string;
  type?: 'text' | 'html';
  maxLength?: number;
  className?: string;
}

const SafeContent: React.FC<SafeContentProps> = ({ 
  content, 
  type = 'text', 
  maxLength = 10000,
  className 
}) => {
  if (!content || typeof content !== 'string') {
    return null;
  }

  // Truncate content if it exceeds max length
  const truncatedContent = content.length > maxLength 
    ? content.substring(0, maxLength) + '...' 
    : content;

  if (type === 'html') {
    // For HTML content, sanitize and render dangerously
    const sanitizedHTML = sanitizeHTML(truncatedContent);
    
    return (
      <div 
        className={className}
        dangerouslySetInnerHTML={{ __html: sanitizedHTML }}
      />
    );
  }

  // For plain text, encode to prevent XSS
  const safeText = encodeHTML(truncatedContent);
  
  return (
    <div className={className}>
      {safeText}
    </div>
  );
};

export default SafeContent;