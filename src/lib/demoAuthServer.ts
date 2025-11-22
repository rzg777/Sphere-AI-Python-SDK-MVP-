import { AdminSummary, AuthTokens, User } from './auth.types';
import {
  base64UrlEncode,
  base64UrlDecode,
  bytesToUtf8,
  hmacSha256,
  timingSafeEqual,
  utf8ToBytes,
} from './crypto';

interface DemoUserRecord extends User {
  passwordHash: string;
}

interface TokenPayload extends User {
  sub: string;
  exp: number;
  iat: number;
  type: 'access' | 'refresh';
}

const DEMO_SECRET = import.meta.env?.VITE_DEMO_AUTH_SECRET ?? 'demo-secret-key';
const PASSWORD_SALT = import.meta.env?.VITE_DEMO_PASSWORD_SALT ?? 'demo-password-salt';

const ACCESS_TOKEN_TTL_SECONDS = 60 * 15; // 15 minutes
const REFRESH_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days

const DEMO_USERS: DemoUserRecord[] = [
  {
    id: '1',
    email: 'user@example.com',
    name: 'Demo User',
    role: 'user',
    passwordHash: '',
  },
  {
    id: '2',
    email: 'admin@example.com',
    name: 'Admin User',
    role: 'admin',
    passwordHash: '',
  },
];

const refreshTokenStore = new Map<string, string>();

const applyPasswordHashes = () => {
  if (DEMO_USERS[0].passwordHash && DEMO_USERS[1].passwordHash) {
    return;
  }
  DEMO_USERS[0].passwordHash = hashPassword('password123');
  DEMO_USERS[1].passwordHash = hashPassword('admin123');
};

const hashPassword = (password: string): string => {
  const key = utf8ToBytes(PASSWORD_SALT);
  const digest = hmacSha256(key, utf8ToBytes(password));
  return base64UrlEncode(digest);
};

const createHeader = (): string => base64UrlEncode(utf8ToBytes(JSON.stringify({ alg: 'HS256', typ: 'JWT' })));

const signToken = (payload: TokenPayload): string => {
  const header = createHeader();
  const body = base64UrlEncode(utf8ToBytes(JSON.stringify(payload)));
  const signatureBytes = hmacSha256(utf8ToBytes(DEMO_SECRET), utf8ToBytes(`${header}.${body}`));
  const signature = base64UrlEncode(signatureBytes);
  return `${header}.${body}.${signature}`;
};

const verifyToken = (token: string): TokenPayload => {
  const [header, body, signature] = token.split('.');
  if (!header || !body || !signature) {
    throw new Error('Malformed token');
  }
  const expectedSignature = base64UrlEncode(
    hmacSha256(utf8ToBytes(DEMO_SECRET), utf8ToBytes(`${header}.${body}`))
  );
  if (!timingSafeEqual(signature, expectedSignature)) {
    throw new Error('Invalid token signature');
  }
  const payload = JSON.parse(bytesToUtf8(base64UrlDecode(body))) as TokenPayload;
  if (payload.exp <= Math.floor(Date.now() / 1000)) {
    throw new Error('Token expired');
  }
  return payload;
};

const sanitizeUser = (user: DemoUserRecord): User => ({
  id: user.id,
  email: user.email,
  name: user.name,
  role: user.role,
});

const buildTokenPayload = (user: DemoUserRecord, type: 'access' | 'refresh'): TokenPayload => {
  const now = Math.floor(Date.now() / 1000);
  return {
    ...sanitizeUser(user),
    sub: user.id,
    iat: now,
    exp: now + (type === 'access' ? ACCESS_TOKEN_TTL_SECONDS : REFRESH_TOKEN_TTL_SECONDS),
    type,
  };
};

const simulateNetworkDelay = async () => new Promise((resolve) => setTimeout(resolve, 300));

const getUserByEmail = (email: string): DemoUserRecord | undefined =>
  DEMO_USERS.find((user) => user.email === email);

const getUserById = (id: string): DemoUserRecord | undefined =>
  DEMO_USERS.find((user) => user.id === id);

const issueTokens = (user: DemoUserRecord): AuthTokens => {
  const accessToken = signToken(buildTokenPayload(user, 'access'));
  const refreshToken = signToken(buildTokenPayload(user, 'refresh'));
  refreshTokenStore.set(refreshToken, user.id);
  return { accessToken, refreshToken };
};

const verifyAccessToken = (token: string): DemoUserRecord => {
  const payload = verifyToken(token);
  if (payload.type !== 'access') {
    throw new Error('Invalid token type');
  }
  const user = getUserById(payload.sub);
  if (!user) {
    throw new Error('User not found');
  }
  return user;
};

export const demoAuthServer = {
  async login(email: string, password: string) {
    applyPasswordHashes();
    await simulateNetworkDelay();

    const record = getUserByEmail(email);
    if (!record) {
      throw new Error('Invalid email or password');
    }

    if (!timingSafeEqual(record.passwordHash, hashPassword(password))) {
      throw new Error('Invalid email or password');
    }

    const tokens = issueTokens(record);
    return { ...tokens, user: sanitizeUser(record) };
  },

  async getProfile(accessToken: string): Promise<User> {
    await simulateNetworkDelay();
    const user = verifyAccessToken(accessToken);
    return sanitizeUser(user);
  },

  async refreshSession(refreshToken: string): Promise<AuthTokens> {
    await simulateNetworkDelay();
    const payload = verifyToken(refreshToken);
    if (payload.type !== 'refresh') {
      throw new Error('Invalid refresh token');
    }
    if (!refreshTokenStore.has(refreshToken)) {
      throw new Error('Refresh token revoked');
    }
    const user = getUserById(payload.sub);
    if (!user) {
      throw new Error('User not found');
    }
    refreshTokenStore.delete(refreshToken);
    return issueTokens(user);
  },

  async revokeSession(refreshToken?: string | null) {
    await simulateNetworkDelay();
    if (refreshToken) {
      refreshTokenStore.delete(refreshToken);
    }
  },

  async getAdminSummary(accessToken: string): Promise<AdminSummary> {
    await simulateNetworkDelay();
    const user = verifyAccessToken(accessToken);
    if (user.role !== 'admin') {
      throw new Error('Forbidden');
    }
    return {
      uptime: '99.9%',
      activeUsers: 1234,
      pendingTasks: 12,
      criticalIssues: 0,
    };
  },
};
