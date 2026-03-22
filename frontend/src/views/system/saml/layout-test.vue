<template>
  <div class="layout-test-container">
    <h2>SAML配置页面布局测试</h2>
    
    <div class="test-section">
      <h3>测试数据</h3>
      <p>以下是模拟的SAML配置数据，用于测试表格布局和操作按钮显示：</p>
      
      <div class="mock-table">
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>配置名称</th>
              <th>SP Entity ID</th>
              <th>IdP Entity ID</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in mockData" :key="index">
              <td>{{ index + 1 }}</td>
              <td>
                {{ item.name }}
                <span v-if="item.is_default" class="default-badge">默认</span>
              </td>
              <td class="entity-id">{{ item.entity_id }}</td>
              <td class="entity-id">{{ item.idp_entity_id }}</td>
              <td>
                <span :class="item.status === 'enable' ? 'status-enabled' : 'status-disabled'">
                  {{ item.status === 'enable' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ item.create_time }}</td>
              <td class="action-cell">
                <button class="btn btn-primary">编辑</button>
                <button class="btn btn-success">测试连接</button>
                <button v-if="!item.is_default" class="btn btn-warning">设为默认</button>
                <button class="btn btn-info">查看元数据</button>
                <button class="btn btn-danger">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="test-info">
      <h3>布局修复说明</h3>
      <ul>
        <li>✅ 操作列宽度从300px增加到400px，确保所有按钮都能显示</li>
        <li>✅ 使用固定列(fixed)确保操作列始终可见</li>
        <li>✅ 优化表格高度计算，避免双滚动条问题</li>
        <li>✅ 使用link类型按钮，减少空间占用</li>
        <li>✅ 添加响应式设计，适配不同屏幕尺寸</li>
        <li>✅ 优化按钮间距和排列方式</li>
      </ul>
    </div>

    <div class="navigation-buttons">
      <el-button type="primary" @click="goToSamlConfig">
        查看实际SAML配置页面
      </el-button>
      <el-button @click="goBack">
        返回上一页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const mockData = ref([
  {
    name: 'Azure AD SAML',
    entity_id: 'https://your-domain.com/saml/metadata',
    idp_entity_id: 'https://sts.windows.net/tenant-id/',
    status: 'enable',
    is_default: true,
    create_time: '2024-01-06 17:30:00'
  },
  {
    name: 'ADFS SAML',
    entity_id: 'https://your-domain.com/saml/metadata',
    idp_entity_id: 'http://adfs-server.com/adfs/services/trust',
    status: 'enable',
    is_default: false,
    create_time: '2024-01-06 17:25:00'
  },
  {
    name: '测试SAML配置_1736160934',
    entity_id: 'https://test-domain.com/saml/metadata',
    idp_entity_id: 'https://test-idp.com/metadata',
    status: 'disable',
    is_default: false,
    create_time: '2024-01-06 17:15:34'
  }
])

const goToSamlConfig = () => {
  router.push('/system/saml')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.layout-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.mock-table {
  overflow-x: auto;
  margin: 20px 0;
}

.mock-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mock-table th,
.mock-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid #e4e7ed;
}

.mock-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #606266;
}

.entity-id {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #666;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.default-badge {
  background: #fdf6ec;
  color: #e6a23c;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
}

.status-enabled {
  color: #67c23a;
  font-weight: 500;
}

.status-disabled {
  color: #f56c6c;
  font-weight: 500;
}

.action-cell {
  min-width: 400px;
}

.btn {
  padding: 4px 8px;
  margin: 0 2px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  text-decoration: none;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-success {
  background: #67c23a;
  color: white;
}

.btn-warning {
  background: #e6a23c;
  color: white;
}

.btn-info {
  background: #909399;
  color: white;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

.test-info {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #67c23a;
  border-radius: 8px;
  background: #f0f9ff;
}

.test-info ul {
  margin: 10px 0;
  padding-left: 20px;
}

.test-info li {
  margin: 8px 0;
  line-height: 1.5;
}

.navigation-buttons {
  margin: 30px 0;
  text-align: center;
}

.navigation-buttons .el-button {
  margin: 0 10px;
}

@media (max-width: 768px) {
  .mock-table {
    font-size: 12px;
  }
  
  .btn {
    padding: 2px 4px;
    font-size: 10px;
    margin: 1px;
  }
  
  .action-cell {
    min-width: 300px;
  }
}
</style>