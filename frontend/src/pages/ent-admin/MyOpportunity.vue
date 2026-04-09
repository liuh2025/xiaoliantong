<template>
  <div class="my-opportunity-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商机管理</span>
          <el-button type="primary" @click="openCreateDialog">发布商机</el-button>
        </div>
      </template>

      <el-table :data="opportunities" v-loading="loading" empty-text="暂无商机数据">
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'buy' ? 'warning' : 'success'">
              {{ row.type === 'buy' ? '采购' : '供应' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '上线中' : '已下线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览量" width="90" />
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'active'"
              size="small"
              type="warning"
              @click="handleOffline(row)"
            >下线</el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleRepublish(row)"
            >重新发布</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchData"
          @size-change="fetchData"
        />
      </div>
    </el-card>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑商机' : '发布商机'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="dialogForm.title" placeholder="请输入商机标题" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="dialogForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="采购" value="buy" />
            <el-option label="供应" value="supply" />
          </el-select>
        </el-form-item>
        <el-form-item label="详情描述">
          <el-input
            v-model="dialogForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商机详情"
          />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="dialogForm.contact" placeholder="请输入联系方式" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMyOpportunities,
  updateMyOpportunity,
  offlineMyOpportunity,
  republishMyOpportunity,
} from '../../api/entAdmin'

const loading = ref(false)
const opportunities = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const dialogSaving = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const dialogForm = ref({
  title: '',
  type: 'buy',
  description: '',
  contact: '',
})

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getMyOpportunities({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      opportunities.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载商机列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEdit.value = false
  editId.value = null
  dialogForm.value = { title: '', type: 'buy', description: '', contact: '' }
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = {
    title: row.title || '',
    type: row.type || 'buy',
    description: row.description || '',
    contact: row.contact || '',
  }
  dialogVisible.value = true
}

async function submitDialog() {
  if (!dialogForm.value.title) {
    ElMessage.warning('请输入商机标题')
    return
  }
  dialogSaving.value = true
  try {
    const { data: res } = await updateMyOpportunity(editId.value, dialogForm.value)
    if (res.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '发布成功')
      dialogVisible.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    dialogSaving.value = false
  }
}

async function handleOffline(row) {
  try {
    await ElMessageBox.confirm(
      `确定要下线商机 "${row.title}" 吗？`,
      '下线商机',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await offlineMyOpportunity(row.id)
    if (res.code === 200) {
      ElMessage.success('已下线')
      await fetchData()
    } else {
      ElMessage.error(res.message || '下线失败')
    }
  } catch {
    // cancelled
  }
}

async function handleRepublish(row) {
  try {
    await ElMessageBox.confirm(
      `确定要重新发布商机 "${row.title}" 吗？`,
      '重新发布',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' },
    )
    const { data: res } = await republishMyOpportunity(row.id)
    if (res.code === 200) {
      ElMessage.success('已重新发布')
      await fetchData()
    } else {
      ElMessage.error(res.message || '发布失败')
    }
  } catch {
    // cancelled
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
