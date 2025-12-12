/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*', // Proxy to Backend
            },
            {
                source: '/demo/:path*',
                destination: 'http://localhost:8000/api/demo/:path*', // Proxy demo routes if needed
            },
        ]
    },
}

module.exports = nextConfig
