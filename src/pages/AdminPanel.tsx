"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UserMenu } from '@/components/auth/UserMenu';
import { authService } from '@/lib/auth';
import { MadeWithDyad } from '@/components/made-with-dyad';
import { Shield, Users, Settings, AlertTriangle } from 'lucide-react';

const AdminPanel: React.FC = () => {
  const user = authService.getCurrentUser();

  return (
    <div className="min-h-screen bg-red-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-red-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
            </div>
            <UserMenu />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Warning Banner */}
          <Card className="bg-yellow-50 border-yellow-200 mb-8">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mr-3" />
                <div>
                  <h3 className="text-lg font-medium text-yellow-800">
                    Administrative Access
                  </h3>
                  <p className="text-yellow-700 mt-1">
                    You are accessing sensitive administrative functions. All actions are logged.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Admin Info */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Administrative Dashboard
            </h2>
            <p className="text-gray-600">
              Logged in as <span className="font-medium">{user?.name}</span> with <span className="font-medium capitalize">{user?.role}</span> privileges
            </p>
          </div>

          {/* Admin Controls Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="mr-2 h-5 w-5" />
                  User Management
                </CardTitle>
                <CardDescription>
                  Manage system users and permissions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Button className="w-full">View All Users</Button>
                  <Button variant="outline" className="w-full">Create New User</Button>
                  <Button variant="outline" className="w-full">Role Management</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="mr-2 h-5 w-5" />
                  System Settings
                </CardTitle>
                <CardDescription>
                  Configure application settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Button className="w-full">General Settings</Button>
                  <Button variant="outline" className="w-full">Security Policies</Button>
                  <Button variant="outline" className="w-full">Backup & Restore</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="mr-2 h-5 w-5" />
                  Security Center
                </CardTitle>
                <CardDescription>
                  Monitor and manage security
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Button className="w-full">Audit Logs</Button>
                  <Button variant="outline" className="w-full">Security Alerts</Button>
                  <Button variant="outline" className="w-full">Access Control</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* System Status */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>
                Current system health and metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">99.9%</div>
                  <div className="text-sm text-green-800">Uptime</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">1,234</div>
                  <div className="text-sm text-blue-800">Active Users</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">12</div>
                  <div className="text-sm text-yellow-800">Pending Tasks</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">0</div>
                  <div className="text-sm text-purple-800">Critical Issues</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      <MadeWithDyad />
    </div>
  );
};

export default AdminPanel;