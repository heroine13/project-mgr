# 项目进度管理系统 - 前端 (Vue 3)

## 技术栈
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **UI库**: Element Plus (Element UI for Vue 3)
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **国际化**: Vue I18n (基于i18next理念)
- **HTTP客户端**: Axios
- **样式**: SCSS + Element Plus主题定制

## 项目结构
```
frontend/
├── public/              # 静态资源
├── src/
│   ├── assets/         # 图片、字体等资源
│   ├── components/     # 公共组件
│   ├── composables/    # Composition API可复用逻辑
│   ├── layouts/        # 布局组件
│   ├── locales/        # 多语言文件
│   ├── router/         # 路由配置
│   ├── services/       # API服务层
│   ├── stores/         # Pinia状态管理
│   ├── styles/         # 全局样式
│   ├── types/          # TypeScript类型定义
│   ├── utils/          # 工具函数
│   ├── views/          # 页面组件
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── .env.development    # 开发环境配置
├── .env.production     # 生产环境配置
├── package.json        # 依赖配置
├── vite.config.js      # Vite配置
└── README.md           # 项目说明
```

## 核心功能模块
### 1. 认证模块
- 登录/注册页面
- JWT令牌管理
- 权限控制组件

### 2. 仪表盘模块
- 项目概览统计
- 任务状态分布
- 团队活动动态

### 3. 任务管理模块
- 任务列表视图（表格/看板）
- 任务详情页面
- 任务创建/编辑表单
- 任务筛选与搜索

### 4. 时间线模块
- 交互式甘特图组件
- 时间线视图
- 里程碑管理

### 5. 文档管理模块
- 文件上传/下载
- 文档预览
- 版本对比

### 6. 问答模块
- Issue列表
- Issue详情与讨论
- 标签与状态管理

## 多语言实现
- 支持中文(zh-CN)和英文(en-US)
- 动态语言切换
- 翻译文件按模块分割
- 翻译内容后台管理界面

## 开发环境配置
```bash
# 安装依赖
npm install

# 开发环境运行
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

## 代码规范
- 使用ESLint + Prettier
- 组件采用Composition API
- 类型优先（TypeScript推荐）
- 响应式设计适配