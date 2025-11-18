"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useLoginValidation } from '@/hooks/useValidation';
import FormField from '@/components/ui/FormField';
import { authService } from '@/lib/auth';
import { showSuccess, showError } from '@/utils/toast';

interface SecureLoginFormProps {
  onSuccess: () => void;
  onSwitchToRegister?: () => void;
}

const SecureLoginForm: React.FC<SecureLoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
  } = useLoginValidation(async (data) => {
    try {
      await authService.login(data.email, data.password);
      showSuccess('Login successful!');
      onSuccess();
    } catch (error) {
      showError(error instanceof Error ? error.message : 'Login failed');
    }
  });

  const handleDemoLogin = async (email: string, password: string) => {
    try {
      await authService.login(email, password);
      showSuccess('Demo login successful!');
      onSuccess();
    } catch (error) {
      showError('Demo login failed');
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Secure Login</CardTitle>
        <CardDescription>
          Credentials are verified server-side and demo accounts are
          read-only fixtures.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormField
            label="Email"
            name="email"
            type="email"
            placeholder="user@example.com"
            error={errors.email?.message}
            register={register}
            required
          />
          
          <FormField
            label="Password"
            name="password"
            type="password"
            placeholder="Enter your password"
            error={errors.password?.message}
            register={register}
            required
          />
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isSubmitting || !isValid}
          >
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <div className="mt-6 space-y-3">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Demo Accounts
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <Button 
              variant="outline" 
              onClick={() => handleDemoLogin('user@example.com', 'password123')}
              disabled={isSubmitting}
            >
              User Demo
            </Button>
            <Button 
              variant="outline"
              onClick={() => handleDemoLogin('admin@example.com', 'admin123')}
              disabled={isSubmitting}
            >
              Admin Demo
            </Button>
          </div>
        </div>

        {onSwitchToRegister && (
          <div className="mt-4 text-center text-sm">
            Don't have an account?{' '}
            <Button variant="link" className="p-0" onClick={onSwitchToRegister}>
              Sign up
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SecureLoginForm;