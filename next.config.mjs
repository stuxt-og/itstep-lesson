/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
  },
};

export default nextConfig;