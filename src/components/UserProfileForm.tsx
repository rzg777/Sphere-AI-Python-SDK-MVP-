"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useProfileValidation } from '@/hooks/useValidation';
import FormField from '@/components/ui/FormField';
import { showSuccess, showError } from '@/utils/toast';
import { authService } from '@/lib/auth';

interface UserProfileFormProps {
  onSuccess?: () => void;
}

const UserProfileForm: React.FC<UserProfileFormProps> = ({ onSuccess }) => {
  const currentUser = authService.getCurrentUser();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
  } = useProfileValidation(
    {
      name: currentUser?.name || '',
      email: currentUser?.email || '',
      avatar: '',
    },
    async (data) => {
      try {
        // In a real app, this would call an API to update the profile
        console.log('Updating profile with validated data:', data);
        showSuccess('Profile updated successfully!');
        onSuccess?.();
      } catch (error) {
        showError('Failed to update profile');
      }
    }
  );

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Update Profile</CardTitle>
        <CardDescription>
          Update your profile information securely
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormField
            label="Full Name"
            name="name"
            type="text"
            placeholder="Enter your full name"
            error={errors.name?.message}
            register={register}
            required
          />
          
          <FormField
            label="Email"
            name="email"
            type="email"
            placeholder="your.email@example.com"
            error={errors.email?.message}
            register={register}
            required
          />
          
          <FormField
            label="Avatar URL"
            name="avatar"
            type="url"
            placeholder="https://example.com/avatar.jpg"
            error={errors.avatar?.message}
            register={register}
          />
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isSubmitting || !isValid}
          >
            {isSubmitting ? 'Updating...' : 'Update Profile'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default UserProfileForm;