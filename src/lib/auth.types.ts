export type UserRole = 'user' | 'admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface AdminSummary {
  uptime: string;
  activeUsers: number;
  pendingTasks: number;
  criticalIssues: number;
}
