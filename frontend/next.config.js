/** @type {import('next').NextConfig} */
const nextConfig = {};
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        hostname: "pixpursuit.ams3.digitaloceanspaces.com"
      }
    ]
  },
};
