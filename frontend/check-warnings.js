#!/usr/bin/env node

/**
 * 前端警告检查脚本
 * 用于验证警告修复效果
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 检查前端警告修复状态...\n');

const checks = [
  {
    name: 'Sass 配置检查',
    check: () => {
      const viteConfig = fs.readFileSync('vite.config.ts', 'utf8');
      return viteConfig.includes('api: \'modern-compiler\'') && 
             viteConfig.includes('silenceDeprecations');
    }
  },
  {
    name: 'SCSS @import 替换检查',
    check: () => {
      const commonScss = fs.readFileSync('src/assets/style/common.scss', 'utf8');
      const themeScss = fs.readFileSync('src/theme/index.scss', 'utf8');
      return !commonScss.includes('@import') && !themeScss.includes('@import');
    }
  },
  {
    name: 'TypeScript 配置检查',
    check: () => {
      const tsConfig = fs.readFileSync('tsconfig.json', 'utf8');
      return !tsConfig.includes('element-plus/global') && 
             tsConfig.includes('skipLibCheck');
    }
  },
  {
    name: 'package.json 依赖检查',
    check: () => {
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      return packageJson.devDependencies['sass-embedded'] !== undefined;
    }
  }
];

let allPassed = true;

checks.forEach((check, index) => {
  try {
    const result = check.check();
    const status = result ? '✅' : '❌';
    console.log(`${index + 1}. ${check.name}: ${status}`);
    if (!result) allPassed = false;
  } catch (error) {
    console.log(`${index + 1}. ${check.name}: ❌ (检查失败: ${error.message})`);
    allPassed = false;
  }
});

console.log('\n' + '='.repeat(50));

if (allPassed) {
  console.log('🎉 所有检查通过！警告修复完成。');
  console.log('\n下一步:');
  console.log('1. 运行 npm run dev 启动项目');
  console.log('2. 检查控制台是否还有 Sass 弃用警告');
  console.log('3. 如果仍有警告，请运行 fix-warnings.bat 重新安装依赖');
} else {
  console.log('❌ 部分检查未通过，请检查修复内容。');
  console.log('\n建议:');
  console.log('1. 确保所有文件修改已保存');
  console.log('2. 运行 fix-warnings.bat 重新安装依赖');
  console.log('3. 重新运行此检查脚本');
}

console.log('\n预期解决的警告:');
console.log('• Sass @import rules are deprecated');
console.log('• The legacy JS API is deprecated');
console.log('• util._extend API is deprecated');
console.log('• TypeScript 类型定义错误');