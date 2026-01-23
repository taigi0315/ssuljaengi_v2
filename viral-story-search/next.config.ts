import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/webtoon/:path*',
        destination: 'http://127.0.0.1:8000/webtoon/:path*',
      },
      {
        source: '/search/:path*',
        destination: 'http://127.0.0.1:8000/search/:path*',
      },
      {
        source: '/story/:path*',
        destination: 'http://127.0.0.1:8000/story/:path*',
      },
      {
        source: '/library/:path*',
        destination: 'http://127.0.0.1:8000/library/:path*',
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:8000/health',
      },
    ];
  },
};

export default nextConfig;
