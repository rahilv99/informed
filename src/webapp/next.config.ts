import type { NextConfig } from "next"
import { join } from "path"

// Import types for webpack
import type { Configuration as WebpackConfig } from "webpack"
import CopyPlugin from "copy-webpack-plugin"

const nextConfig: NextConfig = {
  experimental: {
    ppr: true,
  },
  reactStrictMode: true,
  webpack: (config: WebpackConfig, { isServer }) => {
    // Only run this on the client
    if (!isServer) {
      // Make sure plugins array exists
      config.plugins = config.plugins || []

      // Copy the service worker to the public directory
      config.plugins.push(
        new CopyPlugin({
          patterns: [
            {
              from: join(process.cwd(), "app/service-worker.ts"),
              to: join(process.cwd(), "public/service-worker.js"),
              transform(content) {
                // Use esbuild to transform TypeScript to JavaScript
                const { transformSync } = require("esbuild")
                return transformSync(content.toString(), {
                  loader: "ts",
                  target: "es2020",
                  format: "iife",
                }).code
              },
            },
          ],
        }),
      )
    }
    return config
  },
}

export default nextConfig

