const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // 收集控制台错误
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  // 收集页面错误
  const pageErrors = [];
  page.on('pageerror', err => {
    pageErrors.push(err.message);
  });
  
  const results = {
    timestamp: new Date().toISOString(),
    pages: [],
    consoleErrors: [],
    pageErrors: [],
    bugs: []
  };
  
  const BASE_URL = 'http://localhost:5173';
  
  try {
    // 1. 登录页面测试
    console.log('Testing login page...');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'login', status: 'loaded', url: page.url() });
    
    // 检查登录表单元素
    const usernameInput = await page.$('input[type="text"], input[type="email"], input[name="username"], input[name="email"]');
    const passwordInput = await page.$('input[type="password"]');
    const loginButton = await page.$('button[type="submit"], button:has-text("登录"), button:has-text("登录")');
    
    if (!usernameInput) results.bugs.push({ page: 'login', issue: '找不到用户名输入框' });
    if (!passwordInput) results.bugs.push({ page: 'login', issue: '找不到密码输入框' });
    if (!loginButton) results.bugs.push({ page: 'login', issue: '找不到登录按钮' });
    
    // 执行登录
    if (usernameInput && passwordInput && loginButton) {
      await usernameInput.fill('admin');
      await passwordInput.fill('admin123');
      await loginButton.click();
      await page.waitForTimeout(3000);
      
      if (page.url().includes('/login')) {
        results.bugs.push({ page: 'login', issue: '登录失败，仍然停留在登录页' });
      } else {
        results.pages.push({ page: 'login-success', status: 'redirected', url: page.url() });
      }
    }
    
    // 2. 测试仪表盘
    console.log('Testing dashboard...');
    await page.goto(`${BASE_URL}/dashboard`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'dashboard', status: 'loaded', url: page.url() });
    
    // 检查仪表盘元素
    const dashboardCards = await page.$$('.el-card, .card, [class*="card"]');
    console.log(`Dashboard cards found: ${dashboardCards.length}`);
    
    // 3. 测试项目列表
    console.log('Testing projects page...');
    await page.goto(`${BASE_URL}/projects`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'projects', status: 'loaded', url: page.url() });
    
    // 4. 测试创建项目
    console.log('Testing create project...');
    await page.goto(`${BASE_URL}/projects/new`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'create-project', status: 'loaded', url: page.url() });
    
    // 5. 测试任务列表
    console.log('Testing tasks page...');
    await page.goto(`${BASE_URL}/tasks`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'tasks', status: 'loaded', url: page.url() });
    
    // 6. 测试日历视图
    console.log('Testing calendar...');
    await page.goto(`${BASE_URL}/calendar`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'calendar', status: 'loaded', url: page.url() });
    
    // 7. 测试看板视图
    console.log('Testing kanban...');
    await page.goto(`${BASE_URL}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'kanban', status: 'loaded', url: page.url() });
    
    // 8. 测试团队协作
    console.log('Testing team...');
    await page.goto(`${BASE_URL}/team`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'team', status: 'loaded', url: page.url() });
    
    // 9. 测试文档管理
    console.log('Testing documents...');
    await page.goto(`${BASE_URL}/documents`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'documents', status: 'loaded', url: page.url() });
    
    // 10. 测试统计报表
    console.log('Testing statistics...');
    await page.goto(`${BASE_URL}/statistics`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'statistics', status: 'loaded', url: page.url() });
    
    // 11. 测试增强报表
    console.log('Testing reports...');
    await page.goto(`${BASE_URL}/reports`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'reports', status: 'loaded', url: page.url() });
    
    // 12. 测试资源管理
    console.log('Testing resources...');
    await page.goto(`${BASE_URL}/resources`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'resources', status: 'loaded', url: page.url() });
    
    // 13. 测试问题追踪
    console.log('Testing issues...');
    await page.goto(`${BASE_URL}/issues`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'issues', status: 'loaded', url: page.url() });
    
    // 14. 测试工作流
    console.log('Testing workflow...');
    await page.goto(`${BASE_URL}/workflow`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'workflow', status: 'loaded', url: page.url() });
    
    // 15. 测试通知中心
    console.log('Testing notifications...');
    await page.goto(`${BASE_URL}/notifications`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'notifications', status: 'loaded', url: page.url() });
    
    // 16. 测试用户管理
    console.log('Testing user management...');
    await page.goto(`${BASE_URL}/users`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'users', status: 'loaded', url: page.url() });
    
    // 17. 测试权限管理
    console.log('Testing permissions...');
    await page.goto(`${BASE_URL}/permissions`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'permissions', status: 'loaded', url: page.url() });
    
    // 18. 测试AI助手
    console.log('Testing AI assistant...');
    await page.goto(`${BASE_URL}/ai`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'ai', status: 'loaded', url: page.url() });
    
    // 19. 测试备份管理
    console.log('Testing backup...');
    await page.goto(`${BASE_URL}/backup`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'backup', status: 'loaded', url: page.url() });
    
    // 20. 测试审计日志
    console.log('Testing audit...');
    await page.goto(`${BASE_URL}/audit`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'audit', status: 'loaded', url: page.url() });
    
    // 21. 测试翻译管理
    console.log('Testing i18n...');
    await page.goto(`${BASE_URL}/i18n`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'i18n', status: 'loaded', url: page.url() });
    
    // 22. 测试系统设置
    console.log('Testing settings...');
    await page.goto(`${BASE_URL}/settings`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'settings', status: 'loaded', url: page.url() });
    
    // 23. 测试项目模板
    console.log('Testing templates...');
    await page.goto(`${BASE_URL}/templates`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'templates', status: 'loaded', url: page.url() });
    
    // 24. 测试外部联系人
    console.log('Testing external contacts...');
    await page.goto(`${BASE_URL}/external`, { waitUntil: 'networkidle', timeout: 30000 });
    results.pages.push({ page: 'external', status: 'loaded', url: page.url() });
    
    // 记录控制台错误
    results.consoleErrors = consoleErrors;
    results.pageErrors = pageErrors;
    
    if (consoleErrors.length > 0) {
      consoleErrors.forEach(err => {
        results.bugs.push({ page: 'global', issue: `Console Error: ${err}` });
      });
    }
    
    if (pageErrors.length > 0) {
      pageErrors.forEach(err => {
        results.bugs.push({ page: 'global', issue: `Page Error: ${err}` });
      });
    }
    
  } catch (error) {
    results.bugs.push({ page: 'error', issue: error.message });
    console.error('Test error:', error);
  }
  
  await browser.close();
  
  // 输出结果
  console.log('\n=== TEST RESULTS ===\n');
  console.log(JSON.stringify(results, null, 2));
  
  // 保存结果到文件
  const fs = require('fs');
  fs.writeFileSync('/root/.openclaw/workspace/project-mgr/test-results.json', JSON.stringify(results, null, 2));
  
})();