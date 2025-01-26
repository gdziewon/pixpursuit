/** @type {import('next').NextConfig} */
const nextConfig = {};

const url = new URL(process.env.DO_SPACE_ENDPOINT);
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        hostname: url.hostname,
      }
    ]
  },
};
