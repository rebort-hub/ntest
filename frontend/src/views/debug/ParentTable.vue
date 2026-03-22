<template>
  <el-table :data="tableData" style="width: 100%" @expand-change="onExpand">
    <el-table-column type="expand">
      <template #default="props">
        <child-table :data="props.row.children" />
      </template>
    </el-table-column>
    <el-table-column prop="date" label="日期" width="180"></el-table-column>
    <el-table-column prop="name" label="姓名" width="180"></el-table-column>
    <el-table-column prop="address" label="地址"></el-table-column>
  </el-table>
</template>

<script>
import ChildTable from './RecursiveList.vue';

export default {
  components: {
    ChildTable,
  },
  data() {
    return {
      tableData: [
        {
          date: '2016-05-03',
          name: 'Tom',
          address: 'No. 189, Grove St, Los Angeles',
          children: [], // Initially empty, will be filled when row expands
        },
        // Add more rows as needed
      ],
    };
  },
  methods: {
    onExpand(row, expanded) {
      if (expanded) {
        if (row.children.length === 0) {
          // Simulate an API call to fetch child data
          setTimeout(() => {
            row.children.push({
              date: '2016-05-04',
              name: 'Jerry',
              address: 'No. 200, Grove St, Los Angeles',
            });
            // Force update
            this.tableData = [...this.tableData];
          }, 500);
        }
      }
    },
  },
};
</script>
