"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useTextInputValidation } from '@/hooks/useValidation';
import { showSuccess, showError } from '@/utils/toast';

interface CommentFormProps {
  onSubmit: (content: string) => Promise<void>;
  placeholder?: string;
  buttonText?: string;
}

const CommentForm: React.FC<CommentFormProps> = ({ 
  onSubmit, 
  placeholder = "Add a comment...",
  buttonText = "Post Comment"
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
    reset,
  } = useTextInputValidation(async (data) => {
    try {
      await onSubmit(data.content);
      showSuccess('Comment posted successfully!');
      reset();
    } catch (error) {
      showError('Failed to post comment');
    }
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Comment</CardTitle>
        <CardDescription>
          Share your thoughts securely
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Textarea
              placeholder={placeholder}
              {...register('content')}
              className={errors.content ? 'border-red-500' : ''}
              rows={4}
            />
            {errors.content && (
              <p className="text-sm text-red-600">{errors.content.message}</p>
            )}
          </div>
          
          <Button 
            type="submit" 
            disabled={isSubmitting || !isValid}
          >
            {isSubmitting ? 'Posting...' : buttonText}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CommentForm;