import { ConfigEnv, UserConfigExport } from 'vite'
import vue from '@vitejs/plugin-vue'
// @ts-ignore
// import {vitePluginSvg} from "@webxrd/vite-plugin-svg"
import { resolve } from 'path'

const pathResolve = (dir: string): any => {
  return resolve(__dirname, ".", dir)
}

const alias: Record<string, string> = {
  '@': pathResolve("src")
}

/**
 * @description-en vite document address
 * @description-cn vite官网
 * https://vitejs.cn/config/ */
export default ({ command }: ConfigEnv): UserConfigExport => {
  const prodMock = true;
  return {
    base: '/',
    resolve: {
      alias
    },
    define: {
      // 为了兼容一些使用 process.env 的第三方库
      'process.env': {}
    },
    server: {
      port: 8016,
      host: '0.0.0.0',
      open: true,
      proxy: {
        // 后端资源访问方式
        '/api/': {
          target: 'http://127.0.0.1:8018',
          changeOrigin: true
        }
      },
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'echarts': ['echarts']
          }
        }
      },
      // Vite 5.x 中使用 minify 和 terserOptions 来配置压缩
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      }
    },
    plugins: [
      vue(),
      // vitePluginSvg({
      //   // 必要的。必须是绝对路径组成的数组。
      //   iconDirs: [
      //       resolve(__dirname, 'src/assets/svg'),
      //   ],
      //   // 必要的。入口script
      //   main: resolve(__dirname, 'src/main.js'),
      //   symbolIdFormat: 'icon-[name]'
      // }),
    ],
    css: {
      preprocessorOptions: {
        scss: {
          // 静默所有弃用警告
          silenceDeprecations: ['legacy-js-api', 'import', 'global-builtin', 'color-functions'],
          // 使用 legacy API 以避免兼容性问题
          api: 'legacy',
          // 全局变量注入（如果需要）
          additionalData: `
            // 全局 SCSS 变量可以在这里定义
          `
        }
      },
      postcss: {
        plugins: [
            {
              postcssPlugin: 'internal:charset-removal',
              AtRule: {
                charset: (atRule) => {
                  if (atRule.name === 'charset') {
                    atRule.remove();
                  }
                }
              }
            }
        ],
      },
    }
  };
}
