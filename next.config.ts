/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow development from 127.0.0.1 (Safari workaround)
  allowedDevOrigins: ['127.0.0.1', 'localhost'],
  
  // Enable React Strict Mode for better development experience
  reactStrictMode: true,
  
  // Allow images from external domains (if needed)
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
};

export default nextConfig;
