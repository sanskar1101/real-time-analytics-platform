import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // standalone is for Docker self-hosting; Vercel handles its own output format
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
