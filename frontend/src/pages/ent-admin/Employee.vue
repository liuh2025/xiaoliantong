<template>
  <div class="employee-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="openCreateDialog">新增员工</el-button>
        </div>
      </template>

      <el-table :data="employees" v-loading="loading" empty-text="暂无员工数据">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column prop="role_code" label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.role_code === 'enterprise_admin' ? 'danger' : ''">
              {{ roleLabel(row.role_code) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column label="操作" min-width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑角色</el-button>
            <el-button size="small" type="warning" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="handleToggleDisable(row)">
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
            <el-button size="small" type="info" @click="handleUnbind(row)">解绑</el-button>
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
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="480px"
      destroy-on-close
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item v-if="!isEdit" label="手机号" required>
          <el-input v-model="dialogForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="dialogForm.role_code" placeholder="请选择角色" style="width: 100%">
            <el-option label="普通员工" value="employee" />
            <el-option label="管理员" value="enterprise_admin" />
          </el-select>
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
  getEmployeeList,
  createEmployee,
  updateEmployee,
  resetEmployeePassword,
  disableEmployee,
  unbindEmployee,
} from '../../api/entAdmin'

const loading = ref(false)
const employees = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const dialogSaving = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const dialogForm = ref({
  phone: '',
  role_code: 'employee',
})

const roleLabelMap = {
  enterprise_admin: '管理员',
  employee: '普通员工',
}

function roleLabel(code) {
  return roleLabelMap[code] || code
}

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getEmployeeList({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      employees.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载员工列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEdit.value = false
  editId.value = null
  dialogForm.value = { phone: '', role_code: 'employee' }
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = { role_code: row.role_code }
  dialogVisible.value = true
}

async function submitDialog() {
  dialogSaving.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateEmployee(editId.value, dialogForm.value)
    } else {
      if (!dialogForm.value.phone) {
        ElMessage.warning('请输入手机号')
        return
      }
      res = await createEmployee(dialogForm.value)
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

async function handleResetPassword(row) {
  try {
    await ElMessageBox.confirm(
      `确定要重置员工 "${row.username || row.phone}" 的密码吗？`,
      '重置密码',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await resetEmployeePassword(row.id)
    if (res.code === 200) {
      ElMessage.success('密码已重置')
    } else {
      ElMessage.error(res.message || '重置失败')
    }
  } catch {
    // cancelled
  }
}

async function handleToggleDisable(row) {
  const action = row.is_active ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}员工 "${row.username || row.phone}" 吗？`,
      action + '员工',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await disableEmployee(row.id)
    if (res.code === 200) {
      ElMessage.success(`${action}成功`)
      await fetchData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    // cancelled
  }
}

async function handleUnbind(row) {
  try {
    await ElMessageBox.confirm(
      `确定要解绑员工 "${row.username || row.phone}" 吗？此操作不可恢复。`,
      '解绑员工',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await unbindEmployee(row.id)
    if (res.code === 200) {
      ElMessage.success('解绑成功')
      await fetchData()
    } else {
      ElMessage.error(res.message || '解绑失败')
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
