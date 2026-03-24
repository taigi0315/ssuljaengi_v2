import type { NextConfig } from 'next';

// Set NEXT_STATIC_EXPORT=true at build time to produce a GitHub Pages-compatible
// static export (output: 'export').  In that mode the Next.js dev-proxy rewrites
// are omitted because the browser makes requests directly to NEXT_PUBLIC_API_URL.
const isStaticExport = process.env.NEXT_STATIC_EXPORT === 'true';

const nextConfig: NextConfig = {
  ...(isStaticExport
    ? {
        output: 'export',
        // Repo-name basePath so GitHub Pages serves from /ssuljaengi_v2/
        basePath: '/ssuljaengi_v2',
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : {
        // Dev / EC2: proxy API calls to the local backend so that
        // NEXT_PUBLIC_API_URL is not required during local development.
        async rewrites() {
          return [
            { source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' },
            { source: '/webtoon/:path*', destination: 'http://127.0.0.1:8000/webtoon/:path*' },
            { source: '/search/:path*', destination: 'http://127.0.0.1:8000/search/:path*' },
            { source: '/story/:path*', destination: 'http://127.0.0.1:8000/story/:path*' },
            { source: '/library/:path*', destination: 'http://127.0.0.1:8000/library/:path*' },
            { source: '/health', destination: 'http://127.0.0.1:8000/health' },
          ];
        },
      }),
};

export default nextConfig;
