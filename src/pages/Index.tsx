"use client";

import { MadeWithDyad } from "@/components/made-with-dyad";
import UserProfileForm from "@/components/UserProfileForm";
import CommentForm from "@/components/CommentForm";
import SafeContent from "@/components/SafeContent";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const Index = () => {
  const [comments, setComments] = useState<string[]>([]);

  const handleCommentSubmit = async (content: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setComments(prev => [...prev, content]);
  };

  const dangerousContent = `<script>alert('XSS Attack!')</script><p>This is safe content</p>`;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Secure Application Demo</h1>
          <p className="text-xl text-gray-600">
            Built with comprehensive input validation and XSS protection
          </p>
        </div>

        {/* Security Features Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Secure Login Form */}
          <Card>
            <CardHeader>
              <CardTitle>Secure Authentication</CardTitle>
              <CardDescription>
                Login form with real-time validation and XSS protection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Try entering invalid data to see validation in action
              </p>
              <Button 
                onClick={() => window.location.href = '/login'}
                className="w-full"
              >
                Go to Secure Login
              </Button>
            </CardContent>
          </Card>

          {/* Safe Content Rendering */}
          <Card>
            <CardHeader>
              <CardTitle>Safe Content Rendering</CardTitle>
              <CardDescription>
                User-generated content is safely sanitized and rendered
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Dangerous Input:</h4>
                  <code className="text-xs bg-red-50 p-2 rounded block">
                    {dangerousContent}
                  </code>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Safe Output:</h4>
                  <SafeContent 
                    content={dangerousContent} 
                    type="html"
                    className="border p-3 rounded bg-white"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Profile Form */}
          <UserProfileForm />

          {/* Comment System */}
          <Card>
            <CardHeader>
              <CardTitle>Secure Comment System</CardTitle>
              <CardDescription>
                Post comments with content validation and sanitization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CommentForm 
                onSubmit={handleCommentSubmit}
                placeholder="Share your thoughts securely..."
                buttonText="Post Secure Comment"
              />
              
              {comments.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h4 className="font-medium">Recent Comments:</h4>
                  {comments.map((comment, index) => (
                    <SafeContent
                      key={index}
                      content={comment}
                      type="text"
                      className="border p-3 rounded bg-white text-sm"
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Security Summary */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-800">Security Features Implemented</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>Zod schema validation for all inputs</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>React Hook Form with real-time validation</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>DOMPurify HTML sanitization</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>XSS prevention with output encoding</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>SQL injection pattern detection</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>Safe URL validation</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      <MadeWithDyad />
    </div>
  );
};

export default Index;