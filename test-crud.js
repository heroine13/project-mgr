const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const results = {
    timestamp: new Date().toISOString(),
    crudTests: [],
    bugs: []
  };
  
  const BASE_URL = 'http://localhost:5173';
  
  try {
    // 1. 先登录
    console.log('Logging in...');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.fill('input[type="text"], input[name="username"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"], button:has-text("登录")');
    await page.waitForTimeout(3000);
    
    // 2. 测试创建项目
    console.log('Testing create project...');
    await page.goto(`${BASE_URL}/projects/new`, { waitUntil: 'networkidle', timeout: 30000 });
    
    const projectNameInput = await page.$('input[name="name"], input[name="projectName"], input[placeholder*="项目"]');
    if (projectNameInput) {
      await projectNameInput.fill('测试项目-Playwright');
      results.crudTests.push({ feature: '创建项目', status: 'input_found', detail: '项目名称输入框存在' });
    } else {
      results.bugs.push({ feature: '创建项目', issue: '找不到项目名称输入框' });
    }
    
    const createButton = await page.$('button:has-text("创建"), button[type="submit"]');
    if (createButton) {
      await createButton.click();
      await page.waitForTimeout(2000);
      results.crudTests.push({ feature: '创建项目提交', status: 'clicked', detail: '点击了创建按钮' });
    }
    
    // 3. 测试项目列表
    console.log('Testing project list...');
    await page.goto(`${BASE_URL}/projects`, { waitUntil: 'networkidle', timeout: 30000 });
    const projectTable = await page.$('table, .el-table, [class*="table"]');
    if (projectTable) {
      results.crudTests.push({ feature: '项目列表', status: 'loaded', detail: '项目表格已加载' });
    }
    
    // 4. 测试创建任务
    console.log('Testing create task...');
    await page.goto(`${BASE_URL}/tasks/new`, { waitUntil: 'networkidle', timeout: 30000 });
    const taskTitleInput = await page.$('input[name="title"], input[name="taskTitle"], input[placeholder*="任务"]');
    if (taskTitleInput) {
      await taskTitleInput.fill('测试任务-Playwright');
      results.crudTests.push({ feature: '创建任务', status: 'input_found', detail: '任务标题输入框存在' });
    } else {
      results.bugs.push({ feature: '创建任务', issue: '找不到任务标题输入框' });
    }
    
    // 5. 测试日历视图交互
    console.log('Testing calendar interaction...');
    await page.goto(`${BASE_URL}/calendar`, { waitUntil: 'networkidle', timeout: 30000 });
    const calendarCells = await page.$$('.el-calendar-table td, [class*="calendar"] td, .calendar-day');
    console.log(`Calendar cells found: ${calendarCells.length}`);
    
    // 6. 测试看板视图
    console.log('Testing kanban interaction...');
    await page.goto(`${BASE_URL}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    const kanbanColumns = await page.$$('.el-timeline, [class*="column"], [class*="lane"]');
    console.log(`Kanban columns found: ${kanbanColumns.length}`);
    
    // 7. 测试团队协作页面
    console.log('Testing team page...');
    await page.goto(`${BASE_URL}/team`, { waitUntil: 'networkidle', timeout: 30000 });
    const teamMembers = await page.$$('.el-table tr, [class*="member"]');
    console.log(`Team members found: ${teamMembers.length}`);
    
    // 8. 测试用户管理页面
    console.log('Testing user management...');
    await page.goto(`${BASE_URL}/users`, { waitUntil: 'networkidle', timeout: 30000 });
    
    // 检查是否有用户标签页
    const userTabs = await page.$$('.el-tabs__item, [class*="tab"]');
    console.log(`User tabs found: ${userTabs.length}`);
    
    // 检查用户表格
    const userTable = await page.$('table, .el-table');
    if (userTable) {
      results.crudTests.push({ feature: '用户管理', status: 'loaded', detail: '用户表格已加载' });
    }
    
    // 9. 测试权限管理页面
    console.log('Testing permissions...');
    await page.goto(`${BASE_URL}/permissions`, { waitUntil: 'networkidle', timeout: 30000 });
    const permissionTree = await page.$('.el-tree, [class*="tree"]');
    if (permissionTree) {
      results.crudTests.push({ feature: '权限管理', status: 'loaded', detail: '权限树已加载' });
    }
    
    // 10. 测试文档管理
    console.log('Testing documents...');
    await page.goto(`${BASE_URL}/documents`, { waitUntil: 'networkidle', timeout: 30000 });
    const uploadButton = await page.$('input[type="file"], button:has-text("上传")');
    if (uploadButton) {
      results.crudTests.push({ feature: '文档上传', status: 'found', detail: '上传按钮存在' });
    }
    
    // 11. 测试统计报表
    console.log('Testing statistics chart...');
    await page.goto(`${BASE_URL}/statistics`, { waitUntil: 'networkidle', timeout: 30000 });
    const chartElements = await page.$$('.el-chart, [class*="chart"], canvas');
    console.log(`Chart elements found: ${chartElements.length}`);
    
    // 12. 测试资源管理
    console.log('Testing resources...');
    await page.goto(`${BASE_URL}/resources`, { waitUntil: 'networkidle', timeout: 30000 });
    const resourceCards = await page.$$('.el-card, [class*="resource"]');
    console.log(`Resource cards found: ${resourceCards.length}`);
    
    // 13. 测试问题追踪
    console.log('Testing issues...');
    await page.goto(`${BASE_URL}/issues`, { waitUntil: 'networkidle', timeout: 30000 });
    const issueList = await page.$$('.el-card, [class*="issue"]');
    console.log(`Issue items found: ${issueList.length}`);
    
    // 14. 测试工作流
    console.log('Testing workflow...');
    await page.goto(`${BASE_URL}/workflow`, { waitUntil: 'networkidle', timeout: 30000 });
    const workflowList = await page.$$('.el-card, [class*="workflow"]');
    console.log(`Workflow items found: ${workflowList.length}`);
    
    // 15. 测试通知中心
    console.log('Testing notifications...');
    await page.goto(`${BASE_URL}/notifications`, { waitUntil: 'networkidle', timeout: 30000 });
    const notificationItems = await page.$$('.el-card, [class*="notification"]');
    console.log(`Notification items found: ${notificationItems.length}`);
    
    // 16. 测试AI助手
    console.log('Testing AI assistant...');
    await page.goto(`${BASE_URL}/ai`, { waitUntil: 'networkidle', timeout: 30000 });
    const chatInput = await page.$('input[placeholder*="问题"], textarea');
    if (chatInput) {
      results.crudTests.push({ feature: 'AI助手', status: 'loaded', detail: '聊天输入框存在' });
    }
    
    // 17. 测试系统设置
    console.log('Testing settings...');
    await page.goto(`${BASE_URL}/settings`, { waitUntil: 'networkidle', timeout: 30000 });
    const settingsForm = await page.$('form, .el-form');
    if (settingsForm) {
      results.crudTests.push({ feature: '系统设置', status: 'loaded', detail: '设置表单已加载' });
    }
    
    // 18. 测试项目模板
    console.log('Testing templates...');
    await page.goto(`${BASE_URL}/templates`, { waitUntil: 'networkidle', timeout: 30000 });
    const templateCards = await page.$$('.el-card, [class*="template"]');
    console.log(`Template cards found: ${templateCards.length}`);
    
    // 19. 测试外部联系人
    console.log('Testing external contacts...');
    await page.goto(`${BASE_URL}/external`, { waitUntil: 'networkidle', timeout: 30000 });
    const contactTable = await page.$('table, .el-table');
    if (contactTable) {
      results.crudTests.push({ feature: '外部联系人', status: 'loaded', detail: '联系人表格已加载' });
    }
    
  } catch (error) {
    results.bugs.push({ feature: 'error', issue: error.message });
    console.error('Test error:', error);
  }
  
  await browser.close();
  
  console.log('\n=== CRUD TEST RESULTS ===\n');
  console.log(JSON.stringify(results, null, 2));
  
  const fs = require('fs');
  fs.writeFileSync('/root/.openclaw/workspace/project-mgr/test-crud-results.json', JSON.stringify(results, null, 2));
  
})();