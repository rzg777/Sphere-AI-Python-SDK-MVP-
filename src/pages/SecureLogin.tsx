"use client";

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SecureLoginForm from '@/components/auth/SecureLoginForm';
import { MadeWithDyad } from '@/components/made-with-dyad';

const SecureLogin: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLoginSuccess = () => {
    const from = (location.state as any)?.from?.pathname || '/';
    navigate(from, { replace: true });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p className="text-gray-600">Sign in to your account to continue</p>
          </div>
          <SecureLoginForm onSuccess={handleLoginSuccess} />
        </div>
      </div>
      <MadeWithDyad />
    </div>
  );
};

export default SecureLogin;

