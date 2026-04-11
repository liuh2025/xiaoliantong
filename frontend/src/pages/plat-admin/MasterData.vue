<template>
  <div class="master-data-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>基础数据管理</span>
          <el-button type="primary" @click="openCreateDialog(null)">新增根节点</el-button>
        </div>
      </template>

      <el-tabs v-model="activeCategory" @tab-change="fetchData">
        <el-tab-pane label="行业" name="industry" />
        <el-tab-pane label="地区" name="region" />
        <el-tab-pane label="分类" name="category" />
      </el-tabs>

      <el-table
        :data="treeData"
        v-loading="loading"
        empty-text="暂无数据"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="code" label="编码" min-width="140" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="(val) => handleToggleActive(row, val)"
              active-text="启用"
              inactive-text="停用"
              inline-prompt
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openCreateDialog(row)">添加子项</el-button>
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      destroy-on-close
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="dialogForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="dialogForm.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="父节点">
          <el-input :model-value="parentName" disabled />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="dialogForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogSaving" @click="submitDialog">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMasterDataList, createMasterData, updateMasterData, deleteMasterData } from '../../api/platAdmin'

const loading = ref(false)
const activeCategory = ref('industry')
const treeData = ref([])

const dialogVisible = ref(false)
const dialogSaving = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const parentId = ref(null)
const parentName = ref('')
const dialogForm = ref({
  name: '',
  code: '',
  is_active: true,
  parent_id: null,
  category: '',
})

const dialogTitle = computed(() => {
  if (isEdit.value) return '编辑数据'
  return parentId.value ? '添加子项' : '新增根节点'
})

function buildTree(items) {
  const map = {}
  const roots = []
  items.forEach((item) => {
    map[item.id] = { ...item, children: [] }
  })
  items.forEach((item) => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id])
    } else {
      roots.push(map[item.id])
    }
  })
  // Remove empty children arrays for leaf nodes
  function clean(nodes) {
    nodes.forEach((node) => {
      if (node.children.length === 0) {
        delete node.children
      } else {
        clean(node.children)
      }
    })
  }
  clean(roots)
  return roots
}

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getMasterDataList({ category: activeCategory.value, page_size: 1000 })
    if (res.code === 200) {
      const items = res.data.items || res.data || []
      treeData.value = buildTree(items)
    }
  } catch {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog(row) {
  isEdit.value = false
  editId.value = null
  parentId.value = row ? row.id : null
  parentName.value = row ? row.name : '无（根节点）'
  dialogForm.value = {
    name: '',
    code: '',
    is_active: true,
    parent_id: row ? row.id : null,
    category: activeCategory.value,
  }
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  parentId.value = row.parent_id
  parentName.value = row.parent_id ? '上级节点' : '无（根节点）'
  dialogForm.value = {
    name: row.name,
    code: row.code,
    is_active: row.is_active,
  }
  dialogVisible.value = true
}

async function submitDialog() {
  if (!dialogForm.value.name || !dialogForm.value.code) {
    ElMessage.warning('请填写名称和编码')
    return
  }
  dialogSaving.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateMasterData(editId.value, dialogForm.value)
    } else {
      res = await createMasterData(dialogForm.value)
    }
    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      await fetchData()
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    dialogSaving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 "${row.name}" 吗？子节点也会一并删除。`,
      '删除确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await deleteMasterData(row.id)
    if (res.code === 200) {
      ElMessage.success('已删除')
      await fetchData()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch {
    // cancelled
  }
}

async function handleToggleActive(row, val) {
  try {
    const { data: res } = await updateMasterData(row.id, { is_active: val })
    if (res.code === 200) {
      ElMessage.success(val ? '已启用' : '已停用')
      row.is_active = val
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
