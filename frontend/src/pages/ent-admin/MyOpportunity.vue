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
        <el-table-column label="操作" min-width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openContactLogDialog(row)">查看联系方式记录</el-button>
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
      width="700px"
      destroy-on-close
    >
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="商机类型" required>
          <el-radio-group v-model="dialogForm.type" :disabled="isEdit">
            <el-radio value="buy">我要买</el-radio>
            <el-radio value="supply">我能供</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商机标题" required>
          <el-input v-model="dialogForm.title" placeholder="请输入商机标题（最多30字）" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="一级行业" required>
          <el-select
            v-model="dialogForm.industry_1"
            placeholder="请选择一级行业"
            style="width: 100%"
            @change="onDialogIndustryChange"
          >
            <el-option
              v-for="item in industryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="二级行业">
          <el-select
            v-model="dialogForm.industry_2"
            placeholder="请选择二级行业"
            style="width: 100%"
          >
            <el-option
              v-for="item in subIndustryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="业务品类">
          <el-select
            v-model="dialogForm.category"
            placeholder="请选择业务品类"
            style="width: 100%"
          >
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="省份">
          <el-select
            v-model="dialogForm.province"
            placeholder="请选择省份"
            style="width: 100%"
            @change="onDialogProvinceChange"
          >
            <el-option
              v-for="item in provinceOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-select
            v-model="dialogForm.city"
            placeholder="请选择城市"
            style="width: 100%"
          >
            <el-option
              v-for="item in cityOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="业务标签">
          <el-select
            v-model="dialogForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入标签后回车"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="详情描述" required>
          <el-input
            v-model="dialogForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商机详情（至少20字）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogSaving" @click="submitDialog">{{ isEdit ? '保存' : '立即发布' }}</el-button>
      </template>
    </el-dialog>

    <!-- Contact Log Dialog -->
    <el-dialog
      v-model="contactLogVisible"
      title="联系方式获取记录"
      width="600px"
      destroy-on-close
    >
      <el-table :data="contactLogs" v-loading="contactLogLoading" empty-text="暂无获取记录">
        <el-table-column prop="user_name" label="获取人" min-width="100" />
        <el-table-column prop="user_enterprise" label="所属企业" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="获取时间" min-width="170" />
      </el-table>
      <template #footer>
        <el-button @click="contactLogVisible = false">关闭</el-button>
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
import { getDictIndustry, getDictCategory, getDictRegion } from '../../api/enterprise'

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
  industry_1: '',
  industry_2: '',
  category: '',
  province: '',
  city: '',
  tags: [],
  description: '',
})

const industryOptions = ref([])
const subIndustryOptions = ref([])
const categoryOptions = ref([])
const provinceOptions = ref([])
const cityOptions = ref([])

const contactLogVisible = ref(false)
const contactLogLoading = ref(false)
const contactLogs = ref([])

async function loadDictData() {
  try {
    const [indRes, catRes, regRes] = await Promise.all([
      getDictIndustry({ parent_id: '' }),
      getDictCategory(),
      getDictRegion({ parent_id: '' }),
    ])
    if (indRes.data.code === 200) industryOptions.value = indRes.data.data || []
    if (catRes.data.code === 200) categoryOptions.value = catRes.data.data || []
    if (regRes.data.code === 200) provinceOptions.value = regRes.data.data || []
  } catch {
    // silent
  }
}

async function onDialogIndustryChange(val) {
  dialogForm.value.industry_2 = ''
  subIndustryOptions.value = []
  if (!val) return
  try {
    const { data: res } = await getDictIndustry({ parent_id: val })
    if (res.code === 200) subIndustryOptions.value = res.data || []
  } catch {
    // silent
  }
}

async function onDialogProvinceChange(val) {
  dialogForm.value.city = ''
  cityOptions.value = []
  if (!val) return
  try {
    const { data: res } = await getDictRegion({ parent_id: val })
    if (res.code === 200) cityOptions.value = res.data || []
  } catch {
    // silent
  }
}

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
  dialogForm.value = {
    title: '',
    type: 'buy',
    industry_1: '',
    industry_2: '',
    category: '',
    province: '',
    city: '',
    tags: [],
    description: '',
  }
  subIndustryOptions.value = []
  cityOptions.value = []
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = {
    title: row.title || '',
    type: row.type || 'buy',
    industry_1: row.industry_id || '',
    industry_2: row.sub_industry_id || '',
    category: row.category_id || '',
    province: row.province_id || '',
    city: row.city_id || '',
    tags: row.tags || [],
    description: row.description || '',
  }
  // Load sub-options if parent is set
  if (row.industry_id) onDialogIndustryChange(row.industry_id)
  if (row.province_id) onDialogProvinceChange(row.province_id)
  dialogVisible.value = true
}

async function submitDialog() {
  if (!dialogForm.value.title) {
    ElMessage.warning('请输入商机标题')
    return
  }
  if (!isEdit.value && dialogForm.value.description && dialogForm.value.description.length < 20) {
    ElMessage.warning('详情描述至少20字')
    return
  }
  dialogSaving.value = true
  try {
    const payload = { ...dialogForm.value }
    if (isEdit.value) delete payload.type
    const { data: res } = await updateMyOpportunity(editId.value, payload)
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

function openContactLogDialog(row) {
  contactLogs.value = row.contact_logs || []
  contactLogVisible.value = true
}

onMounted(() => {
  loadDictData()
  fetchData()
})
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
