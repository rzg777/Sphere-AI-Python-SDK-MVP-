"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import UserMenu from '@/components/auth/UserMenu';
import { authService } from '@/lib/auth';
import { MadeWithDyad } from '@/components/made-with-dyad';
import { Shield, Users, Settings, BarChart3 } from 'lucide-react';

const Dashboard: React.FC = () => {
  const user = authService.getCurrentUser();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Secure Dashboard</h1>
            </div>
            <UserMenu />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.name}!
            </h2>
            <p className="text-gray-600">
              You are logged in as <span className="font-medium capitalize">{user?.role}</span>
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">1,234</div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$45,231</div>
                <p className="text-xs text-muted-foreground">
                  +18% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">573</div>
                <p className="text-xs text-muted-foreground">
                  +201 since last hour
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Security Score</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">98%</div>
                <p className="text-xs text-muted-foreground">
                  Excellent security posture
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Admin Section (only visible to admins) */}
          {user?.role === 'admin' && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="mr-2 h-5 w-5" />
                  Admin Controls
                </CardTitle>
                <CardDescription>
                  Administrative functions and system management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    You have access to administrative features.
                  </p>
                  <div className="flex space-x-4">
                    <Button>Manage Users</Button>
                    <Button variant="outline">System Settings</Button>
                    <Button variant="outline">View Logs</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Regular User Content */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Your recent account activity and events
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">Login successful</p>
                      <p className="text-sm text-muted-foreground">
                        Just now
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">Profile updated</p>
                      <p className="text-sm text-muted-foreground">
                        2 hours ago
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <Button variant="outline" className="h-auto py-3">
                    <div className="text-left">
                      <div className="font-medium">Edit Profile</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Update your information
                      </div>
                    </div>
                  </Button>
                  <Button variant="outline" className="h-auto py-3">
                    <div className="text-left">
                      <div className="font-medium">Security</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Change password
                      </div>
                    </div>
                  </Button>
                  <Button variant="outline" className="h-auto py-3">
                    <div className="text-left">
                      <div className="font-medium">Notifications</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Manage alerts
                      </div>
                    </div>
                  </Button>
                  <Button variant="outline" className="h-auto py-3">
                    <div className="text-left">
                      <div className="font-medium">Help</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Get support
                      </div>
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      <MadeWithDyad />
    </div>
  );
};

export default Dashboard;