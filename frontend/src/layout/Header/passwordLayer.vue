<template>
  <Layer :layer="layer" @confirm="submit" ref="layerDom">
    <el-form :model="form" :rules="rules" ref="ruleForm" label-width="120px" style="margin-right:30px;">
      <el-form-item label="旧密码：" prop="old_password">
        <el-input v-model="form.old_password" placeholder="请输入旧密码" show-password></el-input>
      </el-form-item>
			<el-form-item label="新密码：" prop="new_password">
			  <el-input v-model="form.new_password" placeholder="请输入新密码" show-password></el-input>
			</el-form-item>
			<el-form-item label="确认密码：" prop="sure_password">
			  <el-input v-model="form.sure_password" placeholder="请输入确认密码" show-password></el-input>
			</el-form-item>
    </el-form>
  </Layer>
</template>

<script lang="ts">
import type { LayerType } from '@/components/layer/index.vue'
import type { Ref } from 'vue'
import type { ElFormItemContext } from 'element-plus/lib/el-form/src/token'
import { defineComponent, ref } from 'vue'
import {ChangePassword} from '@/api/system/user'
import Layer from '@/components/layer/index.vue'
export default defineComponent({
  components: {
    Layer
  },
  props: {
    layer: {
      type: Object,
      default: () => {
        return {
          show: false,
          title: '',
          showButton: true
        }
      }
    }
  },
  setup(props, ctx) {
    const ruleForm: Ref<ElFormItemContext|null> = ref(null)
    const layerDom: Ref<LayerType|null> = ref(null)
    let form = ref({
      old_password: '',
      new_password: '',
      sure_password: ''
    })
    const rules = {
      old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
      new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
      sure_password: [{ required: true, message: '请输入确认密码', trigger: 'blur' }],
    }
    function submit() {
      if (ruleForm.value) {
        ruleForm.value.validate((valid) => {
          if (valid) {
            ChangePassword({
              old_password: form.value.old_password,
              new_password: form.value.new_password,
              sure_password: form.value.sure_password
            }).then(response => {
              if (response){
                layerDom.value && layerDom.value.close()
              }
            })
          } else {
            return false;
          }
        });
      }
    }
    return {
      form,
      rules,
      layerDom,
      ruleForm,
      submit
    }
  }
})
</script>

<style lang="scss" scoped>

</style>
