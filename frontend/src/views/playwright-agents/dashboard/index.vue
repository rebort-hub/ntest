<template>
  <div class="playwright-agents-dashboard">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <h2>AI-Playwright测试控制台</h2>
          <p class="subtitle">让AI成为你的测试工程师，自动规划、生成和修复测试用例</p>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff20">
              <el-icon :size="32" color="#409eff"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_plans || 0 }}</div>
              <div class="stat-label">测试计划</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a20">
              <el-icon :size="32" color="#67c23a"><Tickets /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_codes || 0 }}</div>
              <div class="stat-label">生成代码</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c20">
              <el-icon :size="32" color="#e6a23c"><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_executions || 0 }}</div>
              <div class="stat-label">执行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c20">
              <el-icon :size="32" color="#f56c6c"><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_heals || 0 }}</div>
              <div class="stat-label">自愈修复</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工作流程 -->
    <el-card class="workflow-card">
      <template #header>
        <span class="card-title">AI测试工作流（playwright）</span>
      </template>
      <div class="workflow-steps">
        <div class="step-item" @click="navigateTo('/playwright-agents-planner/index')">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Playwright测试规划（Agent）</h3>
            <p>AI自动探索应用网站，生成完整测试计划</p>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" @click="navigateTo('/playwright-agents-generator/index')">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Playwright代码生成（Agent）</h3>
            <p>将测试计划转换为可执行的Playwright代码</p>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" @click="navigateTo('/playwright-agents/execution')">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Playwright执行测试</h3>
            <p>运行生成的测试代码，获取测试结果</p>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" @click="navigateTo('/playwright-agents-healer/index')">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Playwright自愈修复 (Agent)</h3>
            <p>测试失败时自动分析并修复代码</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 快速开始 -->
    <el-card class="quick-start-card">
      <template #header>
        <span class="card-title">快速开始</span>
      </template>
      <el-steps :active="0" align-center>
        <el-step title="配置LLM" description="确保已配置可用的LLM" />
        <el-step title="创建测试计划" description="输入应用URL，让AI探索" />
        <el-step title="生成测试代码" description="AI自动生成Playwright代码" />
        <el-step title="执行并修复" description="运行测试，失败时自动修复" />
      </el-steps>
      <div class="quick-actions">
        <el-button type="primary" size="small" @click="navigateTo('/playwright-agents-planner/index')">
          开始创建测试计划
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Tickets, VideoPlay, Tools } from '@element-plus/icons-vue'
import { getStatistics } from '@/api/playwright-agents'

const router = useRouter()

const statistics = ref({
  total_plans: 0,
  total_codes: 0,
  total_executions: 0,
  total_heals: 0
})

const navigateTo = (path: string) => {
  router.push(path)
}

const loadStatistics = async () => {
  try {
    const res = await getStatistics()
    if (res.status === 200) {
      statistics.value = res.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped lang="scss">
.playwright-agents-dashboard {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
    
    .header-content {
      .title-section {
        h2 {
          margin: 0 0 10px 0;
          font-size: 28px;
          color: #303133;
        }
        
        .subtitle {
          margin: 0;
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;
    
    .stat-card {
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .stat-content {
        display: flex;
        align-items: center;
        gap: 15px;
        
        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .stat-info {
          flex: 1;
          
          .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #303133;
            margin-bottom: 5px;
          }
          
          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .workflow-card {
    margin-bottom: 20px;
    
    .card-title {
      font-size: 18px;
      font-weight: bold;
    }
    
    .workflow-steps {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 0;
      
      .step-item {
        flex: 1;
        display: flex;
        gap: 15px;
        padding: 20px;
        border-radius: 8px;
        background: #f5f7fa;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          background: #ecf5ff;
          transform: translateY(-3px);
        }
        
        .step-number {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #409eff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: bold;
          flex-shrink: 0;
        }
        
        .step-content {
          flex: 1;
          
          h3 {
            margin: 0 0 8px 0;
            font-size: 16px;
            color: #303133;
          }
          
          p {
            margin: 0;
            font-size: 13px;
            color: #606266;
          }
        }
      }
      
      .step-arrow {
        font-size: 24px;
        color: #909399;
        margin: 0 10px;
      }
    }
  }

  .quick-start-card {
    .card-title {
      font-size: 18px;
      font-weight: bold;
    }
    
    .quick-actions {
      margin-top: 30px;
      text-align: center;
    }
  }
}
</style>
