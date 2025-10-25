export default {
  // 站点基本信息
  title: 'VitePress 演示站点',
  description: '一个使用 VitePress 构建的示例文档网站',
  base: '/vincent-yangyijie.github.io/',
  
  // 构建配置
  build: {
    outDir: '../../dist',
    assetsDir: 'assets'
  },
  
  // 主题配置
  themeConfig: {
    // 导航栏配置
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/' },
      { text: '世界模型', link: '/world-model/' },
      { text: '关于', link: '/about/' }
    ],
    
    // 侧边栏配置
    sidebar: {
      '/guide/': [
        { text: '快速开始', link: '/guide/' },
        { text: '配置指南', link: '/guide/config' },
        { text: '自定义主题', link: '/guide/theme' }
      ],
      '/world-model/': [
        { text: '世界模型的本质', link: '/world-model/' }
      ],
      '/about/': [
        { text: '关于我们', link: '/about/' },
        { text: '联系方式', link: '/about/contact' }
      ]
    },
    
    // 页脚配置
    footer: {
      message: '使用 VitePress 构建',
      copyright: '© 2024 VitePress 演示站点. All rights reserved.'
    },
    
    // 社交链接
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    
    // 搜索配置
    search: {
      provider: 'local',
      placeholder: '搜索',
      allow: ['/guide/']
    }
  },
  
  // Markdown 配置
  markdown: {
    // 启用行号显示
    lineNumbers: true,
    // 配置扩展
    config: (md) => {
      // 可以在这里添加自定义 Markdown 插件
    }
  },
  
  // 插件配置
  plugins: [],
  
  // 自定义样式
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `$color-primary: #3eaf7c;`
        }
      }
    }
  }
}