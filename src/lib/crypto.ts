const BASE64_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const BASE64_LOOKUP: Record<string, number> = BASE64_ALPHABET
  .split('')
  .reduce((acc, char, index) => {
    acc[char] = index;
    return acc;
  }, {} as Record<string, number>);

const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

const K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
  0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
  0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
  0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
  0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
  0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
  0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

const INITIAL_HASH = new Uint32Array([
  0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
  0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]);

const BLOCK_SIZE = 64;

const toUint8Array = (value: ArrayBuffer | Uint8Array): Uint8Array => {
  if (value instanceof Uint8Array) {
    return value;
  }
  return new Uint8Array(value);
};

const concatBytes = (a: Uint8Array, b: Uint8Array): Uint8Array => {
  const output = new Uint8Array(a.length + b.length);
  output.set(a, 0);
  output.set(b, a.length);
  return output;
};

const base64Encode = (bytes: Uint8Array): string => {
  let output = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i];
    const b = i + 1 < bytes.length ? bytes[i + 1] : 0;
    const c = i + 2 < bytes.length ? bytes[i + 2] : 0;

    const triplet = (a << 16) | (b << 8) | c;

    output += BASE64_ALPHABET[(triplet >> 18) & 0x3f];
    output += BASE64_ALPHABET[(triplet >> 12) & 0x3f];
    output += i + 1 < bytes.length ? BASE64_ALPHABET[(triplet >> 6) & 0x3f] : '=';
    output += i + 2 < bytes.length ? BASE64_ALPHABET[triplet & 0x3f] : '=';
  }
  return output;
};

const base64Decode = (value: string): Uint8Array => {
  const clean = value.replace(/[^A-Za-z0-9+/=]/g, '');
  const output: number[] = [];

  for (let i = 0; i < clean.length; i += 4) {
    const chunk =
      (BASE64_LOOKUP[clean[i]] << 18) |
      (BASE64_LOOKUP[clean[i + 1]] << 12) |
      ((BASE64_LOOKUP[clean[i + 2]] ?? 0) << 6) |
      (BASE64_LOOKUP[clean[i + 3]] ?? 0);

    output.push((chunk >> 16) & 0xff);
    if (clean[i + 2] !== '=') {
      output.push((chunk >> 8) & 0xff);
    }
    if (clean[i + 3] !== '=') {
      output.push(chunk & 0xff);
    }
  }

  return new Uint8Array(output);
};

export const base64UrlEncode = (bytes: Uint8Array): string =>
  base64Encode(bytes).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');

export const base64UrlDecode = (value: string): Uint8Array => {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const padding = normalized.length % 4 === 0 ? '' : '='.repeat(4 - (normalized.length % 4));
  return base64Decode(normalized + padding);
};

const rotateRight = (value: number, amount: number): number =>
  (value >>> amount) | (value << (32 - amount));

export const sha256 = (message: Uint8Array): Uint8Array => {
  const bytes = toUint8Array(message);
  const length = bytes.length;
  const bitLengthHi = Math.floor((length * 8) / 0x100000000);
  const bitLengthLo = (length * 8) >>> 0;

  const paddedLength = (((length + 9 + 63) >> 6) << 6);
  const buffer = new ArrayBuffer(paddedLength);
  const padded = new Uint8Array(buffer);
  padded.set(bytes);
  padded[length] = 0x80;

  const view = new DataView(buffer);
  view.setUint32(paddedLength - 8, bitLengthHi, false);
  view.setUint32(paddedLength - 4, bitLengthLo, false);

  const hash = new Uint32Array(INITIAL_HASH);
  const w = new Uint32Array(64);

  for (let i = 0; i < padded.length; i += 64) {
    for (let t = 0; t < 16; t++) {
      w[t] = view.getUint32(i + t * 4, false);
    }
    for (let t = 16; t < 64; t++) {
      const s0 = rotateRight(w[t - 15], 7) ^ rotateRight(w[t - 15], 18) ^ (w[t - 15] >>> 3);
      const s1 = rotateRight(w[t - 2], 17) ^ rotateRight(w[t - 2], 19) ^ (w[t - 2] >>> 10);
      w[t] = (w[t - 16] + s0 + w[t - 7] + s1) >>> 0;
    }

    let a = hash[0];
    let b = hash[1];
    let c = hash[2];
    let d = hash[3];
    let e = hash[4];
    let f = hash[5];
    let g = hash[6];
    let h = hash[7];

    for (let t = 0; t < 64; t++) {
      const S1 = rotateRight(e, 6) ^ rotateRight(e, 11) ^ rotateRight(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + S1 + ch + K[t] + w[t]) >>> 0;
      const S0 = rotateRight(a, 2) ^ rotateRight(a, 13) ^ rotateRight(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (S0 + maj) >>> 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    hash[0] = (hash[0] + a) >>> 0;
    hash[1] = (hash[1] + b) >>> 0;
    hash[2] = (hash[2] + c) >>> 0;
    hash[3] = (hash[3] + d) >>> 0;
    hash[4] = (hash[4] + e) >>> 0;
    hash[5] = (hash[5] + f) >>> 0;
    hash[6] = (hash[6] + g) >>> 0;
    hash[7] = (hash[7] + h) >>> 0;
  }

  const output = new Uint8Array(32);
  const outView = new DataView(output.buffer);
  for (let i = 0; i < hash.length; i++) {
    outView.setUint32(i * 4, hash[i], false);
  }
  return output;
};

export const hmacSha256 = (key: Uint8Array, message: Uint8Array): Uint8Array => {
  let normalizedKey = key.length > BLOCK_SIZE ? sha256(key) : key;
  if (normalizedKey.length < BLOCK_SIZE) {
    const padded = new Uint8Array(BLOCK_SIZE);
    padded.set(normalizedKey);
    normalizedKey = padded;
  }

  const oKeyPad = new Uint8Array(BLOCK_SIZE);
  const iKeyPad = new Uint8Array(BLOCK_SIZE);

  for (let i = 0; i < BLOCK_SIZE; i++) {
    oKeyPad[i] = normalizedKey[i] ^ 0x5c;
    iKeyPad[i] = normalizedKey[i] ^ 0x36;
  }

  const innerHash = sha256(concatBytes(iKeyPad, message));
  return sha256(concatBytes(oKeyPad, innerHash));
};

export const utf8ToBytes = (value: string): Uint8Array => textEncoder.encode(value);
export const bytesToUtf8 = (value: Uint8Array): string => textDecoder.decode(value);

export const timingSafeEqual = (a: string, b: string): boolean => {
  if (a.length !== b.length) {
    return false;
  }
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) {
    mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return mismatch === 0;
};
