/** @type {import('vite').UserConfig} */

import { resolve } from 'path';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import { viteStaticCopy } from 'vite-plugin-static-copy';

// const slIconsPath = './node_modules/@shoelace-style/shoelace/dist/assets/icons';
const mdiIconsPath = './node_modules/@mdi/svg/svg';

export default defineConfig({
  // messes up path, e.g. move content in ./assets inside ./assets/leaf
  base: 'ui',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
  resolve: {
    alias: [
      {
        find: /\/assets\/icons\/(.+)/,
        replacement: `${mdiIconsPath}/$1`,
        //find: /\/assets\/icons\/(.+)/,
        //replacement: resolve(__dirname, `${iconsPath}/$1`),
      },
    ],
  },
  plugins: [
    VitePWA({
      manifest: {
        icons: [
          {
            src: '/ui/icons/leaf-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
    }),
    viteStaticCopy({
      targets: [
        {
          src: mdiIconsPath,
          dest: 'assets',
        },
      ],
    }),
  ],
});
