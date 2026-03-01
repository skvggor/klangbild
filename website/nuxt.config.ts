// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  ssr: true,
  
  nitro: {
    preset: 'node-server'
  },
  
  modules: [
    '@nuxt/ui',
    '@nuxtjs/tailwindcss',
    '@nuxt/content',
    '@nuxt/icon'
  ],
  
  css: [
    '~/assets/styles/global.css'
  ],
  
  content: {
    documentDriven: false
  },
  
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      title: 'klangbild - 4K Audio Visualizer for YouTube',
      meta: [
        { name: 'description', content: 'Generate stunning 4K audio visualizer videos and cover images for YouTube from any MP3 file' },
        { name: 'og:title', content: 'klangbild - 4K Audio Visualizer' },
        { name: 'og:description', content: 'Generate stunning 4K audio visualizer videos and cover images for YouTube' },
        { name: 'og:type', content: 'website' },
        { name: 'og:url', content: 'https://klangbild.skvggor.dev' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'klangbild - 4K Audio Visualizer' },
        { name: 'twitter:description', content: 'Generate stunning 4K audio visualizer videos for YouTube' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32.png' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16.png' },
        { rel: 'manifest', href: '/manifest.json' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap' }
      ],
      script: [
        {
          src: 'https://www.youtube.com/iframe_api',
          defer: true
        }
      ]
    }
  },
  
  compatibilityDate: '2025-01-31'
})
