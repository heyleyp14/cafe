/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // The two app screenshots are 1080x2400 PNGs shown at about 264 CSS px.
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 828, 1080],
    imageSizes: [256, 384, 528],
  },
}

export default nextConfig
