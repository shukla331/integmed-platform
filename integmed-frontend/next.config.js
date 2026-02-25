/** @type {import('next').NextConfig} */
const baseApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost', 'integmed.health'],
  },
  env: {
    NEXT_PUBLIC_API_URL: baseApiUrl,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${baseApiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
