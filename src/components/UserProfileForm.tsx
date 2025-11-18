"use client";

import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useProfileValidation } from '@/hooks/useValidation';
import FormField from '@/components/ui/FormField';
import { showSuccess, showError } from '@/utils/toast';
import { useCurrentUser } from '@/hooks/useCurrentUser';

interface UserProfileFormProps {
  onSuccess?: () => void;
}

const UserProfileForm: React.FC<UserProfileFormProps> = ({ onSuccess }) => {
  const { user: currentUser, loading } = useCurrentUser();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
    reset,
  } = useProfileValidation(
    {
      name: currentUser?.name || '',
      email: currentUser?.email || '',
      avatar: '',
    },
    async (data) => {
      try {
        showSuccess('Profile updated successfully!');
        onSuccess?.();
      } catch (error) {
        showError('Failed to update profile');
      }
    }
  );

  useEffect(() => {
    reset({
      name: currentUser?.name || '',
      email: currentUser?.email || '',
      avatar: '',
    });
  }, [currentUser, reset]);

  if (loading) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Update Profile</CardTitle>
          <CardDescription>Loading your profile...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

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
