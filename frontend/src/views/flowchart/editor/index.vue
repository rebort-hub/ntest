<template>
  <div class="flowchart-container">
    <!-- 左侧功能面板 -->
    <div class="left-panel">
      <!-- 功能按钮区域 -->
      <div class="function-section">
        <div class="section-title">功能操作</div>
        <div class="button-grid">
          <el-button size="small" @click="() => setLine('bezier')">连接线-贝塞尔曲线</el-button>
          <el-button size="small" @click="() => setLine('polyline')">连接线-多段线</el-button>
          <el-button size="small" @click="() => setLine('line')">连接线-直线</el-button>
          <el-button size="small" @click="focusOn">定位到node-1</el-button>
          <el-button size="small" @click="() => lfRef?.undo()">上一步</el-button>
          <el-button size="small" @click="() => lfRef?.redo()">下一步</el-button>
          <el-button size="small" @click="() => lfRef?.clearData()">清空数据</el-button>
          <el-button size="small" @click="changeNodeType">切换节点为圆形</el-button>
          <el-button size="small" @click="cancelEdit">禁止编辑</el-button>
          <el-button size="small" @click="canEdit">允许编辑</el-button>
          <el-button size="small" @click="getGraphData">获取选中节点数据</el-button>
          <el-button size="small" @click="() => lfRef?.zoom(1.2)">放大</el-button>
          <el-button size="small" @click="() => lfRef?.zoom(0.8)">缩小</el-button>
          <el-button size="small" @click="() => lfRef?.zoom(1)">重置缩放</el-button>
          <el-button size="small" @click="checkNode">选中指定节点</el-button>
          <el-button size="small" @click="() => lfRef?.translateCenter()">居中</el-button>
          <el-button size="small" @click="() => lfRef?.fitView()">适应屏幕</el-button>
          <el-button size="small" @click="delNode">删除节点</el-button>
        </div>
      </div>

      <!-- 节点面板 -->
      <div class="nodes-section">
        <div class="section-title">节点面板</div>
        <div class="nodes-grid">
          <div class="dnd-item" @mousedown="handleDragRect">矩形</div>
          <div class="dnd-item" @mousedown="handleDragCircle">圆形</div>
          <div class="dnd-item" @mousedown="handleDragDiamond">菱形</div>
          <div class="dnd-item" @mousedown="handleDragEllipse">椭圆</div>
          <div class="dnd-item" @mousedown="handleDragPolygon">多边形</div>
          <div class="dnd-item" @mousedown="handleDragText">文本</div>
        </div>
      </div>
    </div>

    <!-- 右侧主要内容 -->
    <div class="main-content">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>Graph</span>
            <div class="header-actions">
              <el-button type="success" size="small" @click="saveFlowchart">
                保存流程图
              </el-button>
              <el-button type="primary" size="small" @click="exportFlowchart">
                导出流程图
              </el-button>
            </div>
          </div>
        </template>
        
        <div ref="containerRef" id="graph" class="viewport"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LogicFlow from '@logicflow/core'
import '@logicflow/core/es/index.css'

const data = {
  nodes: [
    {
      id: 'custom-node-1',
      text: 'node-1',
      type: 'rect',
      x: 200,
      y: 150,
      width: 80,
      height: 40
    },
    {
      id: 'custom-node-2',
      text: 'node-2',
      type: 'circle',
      x: 400,
      y: 150,
      r: 30
    }
  ],
  edges: [
    {
      id: 'edge-1',
      sourceNodeId: 'custom-node-1',
      targetNodeId: 'custom-node-2',
      type: 'bezier'
    }
  ]
}

const lfRef = ref<LogicFlow | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const flowId = ref('')

onMounted(() => {
  if (containerRef.value) {
    // 计算画布高度
    const canvasHeight = window.innerHeight - 120 // 最大化画布高度
    
    const lf = new LogicFlow({
      container: containerRef.value,
      height: canvasHeight,
      multipleSelectKey: 'ctrl',
      // 移除禁用工具，允许所有交互
      autoExpand: true,
      adjustEdgeStartAndEnd: true,
      allowRotate: true,
      edgeTextEdit: true,
      keyboard: {
        enabled: true
      },
      partial: true,
      background: {
        color: '#FFFFFF'
      },
      grid: true,
      edgeTextDraggable: true,
      edgeType: 'bezier',
      style: {
        inputText: {
          background: 'black',
          color: 'white'
        }
      },
      idGenerator(type) {
        return type + '_' + Math.random()
      }
    })

    lf.on('graph:rendered', ({ graphModel }) => {
      flowId.value = graphModel?.flowId || ''
    })

    // 渲染数据
    lf.render(data)
    lfRef.value = lf
    
    // 初始化后设置合适的缩放和居中
    setTimeout(() => {
      lf.zoom(1.2) // 放大到120%
      lf.translateCenter() // 居中显示
    }, 100)
  }
})

// 设置箭头
const setLine = (arrowName: string) => {
  const lf = lfRef?.value
  if (lf) {
    const { edges } = lf.getSelectElements()
    edges.forEach(({ id }) => {
      lf.changeEdgeType(id, arrowName)
    })
  }
}

// 定位到指定节点
const focusOn = () => {
  lfRef?.value?.focusOn({
    id: 'custom-node-1'
  })
}

// 切换节点类型
const changeNodeType = () => {
  const lf = lfRef?.value
  if (lf) {
    const { nodes } = lf.getSelectElements()
    nodes.forEach(({ id, type }) => {
      lf.changeNodeType(id, type === 'rect' ? 'circle' : 'rect')
    })
  }
}

// 取消编辑
const cancelEdit = () => {
  const lf = lfRef?.value
  if (lf) {
    const { editConfigModel } = lf.graphModel
    editConfigModel.updateEditConfig({
      isSilentMode: true, // 是否为静默模式
      stopZoomGraph: true, // 禁止缩放画布
      stopScrollGraph: true, // 禁止鼠标滚动移动画布
      stopMoveGraph: true // 禁止拖动画布
    })
  }
}

const canEdit = () => {
  const lf = lfRef?.value
  if (lf) {
    const { editConfigModel } = lf.graphModel
    editConfigModel.updateEditConfig({
      isSilentMode: false,
      stopZoomGraph: false,
      stopScrollGraph: false,
      stopMoveGraph: false
    })
  }
}

// 获取选中节点数据
const getGraphData = () => {
  const lf = lfRef?.value
  if (lf) {
    const { nodes } = lf.getSelectElements()
    console.log(nodes)
  }
}

// 选中指定节点
const checkNode = () => {
  const lf = lfRef?.value
  if (lf) {
    lf.selectElementById('custom-node-1')
  }
}

// 删除节点
const delNode = () => {
  const lf = lfRef?.value
  if (lf) {
    const { nodes } = lf.getSelectElements()
    nodes.forEach(({ id }) => {
      lf.deleteNode(id)
    })
  }
}

const handleDragRect = () => {
  lfRef?.value?.dnd.startDrag({
    type: 'rect',
    text: '矩形'
  })
}

const handleDragCircle = () => {
  lfRef?.value?.dnd.startDrag({
    type: 'circle',
    text: '圆形',
    r: 25
  })
}

const handleDragDiamond = () => {
  lfRef?.value?.dnd.startDrag({
    type: 'diamond',
    text: '菱形'
  })
}

const handleDragEllipse = () => {
  lfRef?.value?.dnd.startDrag({
    type: 'ellipse',
    text: '椭圆',
    properties: {
      rx: 40,
      ry: 80
    }
  })
}

const handleDragPolygon = () => {
  const x = 50, y = 50
  lfRef?.value?.dnd.startDrag({
    type: 'polygon',
    text: '多边形',
    properties: {
      points: [
        [x - 0.205 * 100, y - 0.5 * 100],
        [x + 0.205 * 100, y - 0.5 * 100],
        [x + 0.5 * 100, y - 0.205 * 100],
        [x + 0.5 * 100, y + 0.205 * 100],
        [x + 0.205 * 100, y + 0.5 * 100],
        [x - 0.205 * 100, y + 0.5 * 100],
        [x - 0.5 * 100, y + 0.205 * 100],
        [x - 0.5 * 100, y - 0.205 * 100]
      ]
    }
  })
}

const handleDragText = () => {
  lfRef?.value?.dnd.startDrag({
    type: 'text',
    text: '文本'
  })
}

// 保存流程图
const saveFlowchart = () => {
  const lf = lfRef?.value
  if (lf) {
    const graphData = lf.getGraphData()
    console.log('保存的流程图数据:', graphData)
    // 这里可以调用API保存数据
    ElMessage.success('流程图保存成功')
  }
}

// 导出流程图
const exportFlowchart = () => {
  const lf = lfRef?.value
  if (lf) {
    const graphData = lf.getGraphData()
    const dataStr = JSON.stringify(graphData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `flowchart_${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('流程图导出成功')
  }
}
</script>

<style scoped lang="scss">
.flowchart-container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

// 左侧功能面板
.left-panel {
  width: 300px;
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;

  .function-section, .nodes-section {
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;

    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #409eff;
    }

    .button-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;

      .el-button {
        font-size: 12px;
        padding: 8px 12px;
        height: auto;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    .nodes-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;

      .dnd-item {
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: grab;
        user-select: none;
        width: 70px;
        height: 40px;
        background: #fff;
        border: 2px solid #409eff;
        border-radius: 4px;
        font-size: 12px;
        color: #409eff;
        transition: all 0.3s ease;

        &:hover {
          background-color: #ecf5ff;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
        }

        &:active {
          cursor: grabbing;
          transform: translateY(0);
        }
      }
    }
  }
}

// 主要内容区域
.main-content {
  flex: 1;
  padding: 8px; // 减少内边距
  display: flex;
  flex-direction: column;
  
  .el-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    margin: 0; // 移除外边距
    
    :deep(.el-card__body) {
      flex: 1;
      padding: 4px; // 最小化内边距
    }
    
    :deep(.el-card__header) {
      padding: 12px 16px; // 减少头部内边距
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .viewport {
    width: 100%;
    height: calc(100vh - 120px); // 最大化画布高度
    border: 1px solid #ddd;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .left-panel {
    width: 250px;

    .function-section .button-grid {
      grid-template-columns: 1fr;
    }

    .nodes-section .nodes-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
}

@media (max-width: 768px) {
  .flowchart-container {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;

    .function-section, .nodes-section {
      padding: 12px;
    }
  }
}
</style>