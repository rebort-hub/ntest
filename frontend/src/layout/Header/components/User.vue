<template>
  <div class="user-wrap">
    <el-dropdown>
      <span class="el-dropdown-link">
        <el-avatar class="user-avatar" :size="28">{{ avatarText }}</el-avatar>
        {{ userName }}
        <i class="sfont system-xiala"></i>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="resetPassword">重置密码</el-dropdown-item>
          <el-dropdown-item @click="showPasswordLayer">修改密码</el-dropdown-item>
          <el-dropdown-item @click="loginOut">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    <PasswordLayer :layer="layer" v-if="layer.show" />
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from "vue";
import { useRouter } from "vue-router";
import PasswordLayer from "../passwordLayer.vue";
import { ResetPassword } from "@/api/system/user";

const router = useRouter();
const layer = reactive({ show: false, showButton: true });
const userName = localStorage.getItem("userName") || "User";
const avatarText = computed(() => (userName?.slice(0, 1) || "U").toUpperCase());

const showPasswordLayer = () => {
  layer.show = true;
};

const resetPassword = () => {
  ResetPassword({ id: localStorage.getItem("id") }).then(() => {});
};

const loginOut = () => {
  const itemsToRemove = [
    "id",
    "accessToken",
    "refreshToken",
    "userName",
    "account",
    "permissions",
    "business",
    "isAdmin",
    "platform_name",
    "rememberedAccount"
  ];
  itemsToRemove.forEach(item => localStorage.removeItem(item));
  router.push("/login");
};
</script>

<style lang="scss" scoped>
.user-wrap {
  margin-left: 10px;
}

.el-dropdown-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  padding: 0 10px 0 4px;
  border-radius: 18px;
  color: var(--system-header-breadcrumb-text-color);
  cursor: pointer;
  transition: background-color 0.2s ease;
  &:hover {
    background-color: var(--system-header-item-hover-color);
  }
}

.user-avatar {
  background: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 600;
}
</style>
