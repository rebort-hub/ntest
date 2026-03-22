<template>
  <div class="card" :style="{ 'borderColor': row.color }">
    <div class="card-left">
      <div class="name">{{ row.title }}</div>
      <div class="detail">{{ row.total }}</div>
    </div>
    <div class="card-right">
      <component class="card-icon" :is="getIcon(row.icon)"></component>
    </div>
  </div>
</template>

<script lang="ts" setup>

import * as iconPark from "@icon-park/vue-next";

defineProps({
  row: {
    default: {},
    type: Object
  }
})

const getIcon = (iconName: string) => {
  const normalizedIconName = iconName.charAt(0).toUpperCase() + iconName.slice(1);
  return iconPark[normalizedIconName] || null;
}

</script>

<style lang="scss" scoped>
.card {
  border-radius: 8px;
  overflow: hidden;
  border-left: 4px solid;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background-color: var(--system-page-background);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.12);
  }

  &-left {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding-left: 20px;
    flex: 1;

    .name {
      line-height: 16px;
      color: var(--system-page-tip-color);
      font-size: 12px;
      margin-bottom: 10px;
      font-weight: 500;
    }

    .detail {
      font-size: 20px;
      font-weight: 600;
      color: var(--system-page-color);
      line-height: 1;
    }
  }

  &-right {
    padding-right: 20px;
    display: flex;
    align-items: center;
    justify-content: center;

    .card-icon {
      font-size: 36px;
      font-weight: 900;
      color: #e6e8ef;
      opacity: 0.8;
    }
  }
}

@media screen and (max-width: 1200px) {
  .card {
    height: 90px;
    
    &-left {
      padding-left: 16px;
      
      .name {
        font-size: 11px;
        margin-bottom: 8px;
      }
      
      .detail {
        font-size: 18px;
      }
    }
    
    &-right {
      padding-right: 16px;
      
      .card-icon {
        font-size: 30px;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .card {
    height: 80px;
    
    &-left {
      padding-left: 14px;
      
      .name {
        font-size: 10px;
        margin-bottom: 6px;
      }
      
      .detail {
        font-size: 16px;
      }
    }
    
    &-right {
      padding-right: 14px;
      
      .card-icon {
        font-size: 26px;
      }
    }
  }
}
</style>
