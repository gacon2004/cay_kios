/** @type {import('next').NextConfig} */
const nextConfig = {
  // --- Các cấu hình cũ của bạn ---
  output: 'export',
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },

  // --- Thêm dòng mới vào đây ---
  basePath: '/admin',
};

module.exports = nextConfig;