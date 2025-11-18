"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User, LogOut, Settings, RefreshCcw } from 'lucide-react';
import { authService } from '@/lib/auth';
import { showError, showSuccess } from '@/utils/toast';
import { useCurrentUser } from '@/hooks/useCurrentUser';

const UserMenu: React.FC = () => {
  const { user, loading, refresh } = useCurrentUser();

  const handleLogout = async () => {
    await authService.logout();
    showSuccess('Logged out successfully');
    window.location.href = '/login';
  };

  const handleRefreshSession = async () => {
    try {
      await authService.refreshTokens();
      await refresh();
      showSuccess('Session refreshed');
    } catch (error) {
      showError('Session refresh failed. Please sign in again.');
      await authService.logout();
      window.location.href = '/login';
    }
  };

  if (loading) {
    return (
      <Button variant="ghost" size="sm" className="relative h-8 w-8 rounded-full" disabled>
        <User className="h-4 w-4 animate-pulse" />
      </Button>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="relative h-8 w-8 rounded-full">
          <User className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user.name}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {user.email}
            </p>
            <p className="text-xs leading-none text-muted-foreground capitalize">
              {user.role}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Settings className="mr-2 h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleRefreshSession}>
          <RefreshCcw className="mr-2 h-4 w-4" />
          <span>Refresh session</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserMenu;