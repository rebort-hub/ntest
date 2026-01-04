<template>

  <div class="code-diff">
    <div style="text-align: center;">
      <el-button type="primary" size="small" @click="diffString">字符串对比</el-button>
      <el-button type="primary" size="small" @click="diffJson(false)">json直接对比</el-button>
      <el-button type="primary" size="small" @click="diffJson(true)">json递归排序后对比</el-button>
    </div>
    <el-row>
      <el-col :span="12">
        <div class="code-section">
          <h3>数据1 <span v-show="oldStringError" style="color: red">{{ oldStringError }}</span> </h3>
          <textarea v-model="oldString" placeholder="输入数据1" :style="{height: inputHeight}"></textarea>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="code-section">
          <h3>数据2<span v-show="newStringError" style="color: red">{{ newStringError }}</span> </h3>
          <textarea v-model="newString" placeholder="输入数据2" :style="{height: inputHeight}"></textarea>
        </div>
      </el-col>
    </el-row>

  </div>

  <el-drawer v-model="showDiffRes" title="对比结果" size="80%">
    <div >
      <el-row>
        <el-col :span="12">
          <div style="text-align: center">数据1</div>
        </el-col>
        <el-col :span="12">
          <div style="text-align: center">数据2</div>
        </el-col>
      </el-row>
      <code-diff
          :old-string="oldStringDiff"
          :new-string="newStringDiff"
          :style="{height: inputHeight}"
          output-format="side-by-side"
          language="json"
      />
    </div>
  </el-drawer>

</template>
<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";

const oldString = ref<string>(JSON.stringify({"a":1,"b":[{"b2":2,"a2":2,"c2":3},{"a1":3,"c1":3,"b1":2}]}));
const oldStringDiff = ref<string>('');
const oldStringError = ref<string>('');

const newString = ref<string>(JSON.stringify({"b":[{"c2":3,"b2":3,"a2":2},{"c1":3,"a1":1,"b1":2}],"a":1}));
const newStringDiff = ref<string>('');
const newStringError = ref<string>('');

const showDiffRes = ref(false);

const inputHeight = ref(`${window.innerHeight * 0.67}px`)
const setInputHeight = () => {
  if (window.innerHeight < 800) {  // 小屏
    inputHeight.value = `${window.innerHeight * 0.67}px`
  } else {  // 大屏
    inputHeight.value = `${window.innerHeight * 0.74}px`
  }
}

// 将对象递归排序
const deepSort = (obj) => {
  // 非对象或数组，直接返回
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  // 对数组中的每个元素递归处理，数组顺序也一起改变
  if (Array.isArray(obj)) {
    return obj
        .map(deepSort)  // 先递归处理所有元素
        .sort((a, b) => {
          // 统一排序规则：转换为JSON字符串比较 :ml-citation{ref="5,6" data="citationList"}
          return JSON.stringify(a).localeCompare(JSON.stringify(b));
        });
  }

  // 处理对象
  return Object.keys(obj)
      .sort()  // 按字母顺序排序键
      .reduce((sorted, key) => {
        sorted[key] = deepSort(obj[key]);  // 递归处理属性值
        return sorted;
      }, {});
}

const diffString = () => {
  oldStringDiff.value = oldString.value
  newStringDiff.value = newString.value
  showDiffRes.value = true
}

const diffJson = (isNeedSorted: boolean) => {
  try {
    if (isNeedSorted) {
      oldStringDiff.value = JSON.stringify(deepSort(JSON.parse(oldString.value)), null, 2)
    }else {
      oldStringDiff.value = JSON.stringify(JSON.parse(oldString.value), null, 2)
    }
    oldStringError.value = ""
  }catch(err) {
    oldStringError.value = "不可序列化json，请检查"
    return
  }

  try {
    if (isNeedSorted) {
      newStringDiff.value = JSON.stringify(deepSort(JSON.parse(newString.value)), null, 2)
    }else {
      newStringDiff.value = JSON.stringify(JSON.parse(newString.value), null, 2)
    }
    newStringError.value = ""
  }catch(err) {
    newStringError.value = "不可序列化json，请检查"
    return
  }
  showDiffRes.value = true
}

onMounted(() => {
  setInputHeight()
  window.addEventListener('resize', setInputHeight);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', setInputHeight);
})

</script>
<style>

.code-diff {
  display: flex;
  flex-direction: column;
  margin: 10px;
}

.code-section {
  border: 1px solid #ccc;
  margin: 10px 0;
  padding: 10px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

textarea {
  width: 95%;
  /* height: 500px; */
  height: 900%;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  resize: none; /* 禁止调整大小 */
}

</style>
