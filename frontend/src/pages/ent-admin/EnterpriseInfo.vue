<template>
  <div class="enterprise-info">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>企业信息</span>
          <el-button v-if="!editing" type="primary" @click="startEdit">编辑</el-button>
          <div v-else class="edit-actions">
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="!loading && !enterprise" description="暂无企业信息" />

      <el-descriptions v-else-if="enterprise" :column="2" border>
        <el-descriptions-item label="企业名称" :span="2">
          {{ enterprise.name }}
        </el-descriptions-item>
        <el-descriptions-item label="统一社会信用代码">
          {{ enterprise.credit_code }}
        </el-descriptions-item>
        <el-descriptions-item label="法定代表人">
          {{ enterprise.legal_representative }}
        </el-descriptions-item>
        <el-descriptions-item label="所属行业">
          {{ enterprise.industry_name || enterprise.industry || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="所在地区">
          {{ enterprise.region_name || enterprise.region || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="营业执照">
          <el-image
            v-if="enterprise.business_license"
            :src="enterprise.business_license"
            :preview-src-list="[enterprise.business_license]"
            style="width: 100px; height: 60px"
            fit="cover"
          />
          <span v-else>未上传</span>
        </el-descriptions-item>
        <el-descriptions-item label="认证状态">
          <el-tag :type="authStatusType">{{ authStatusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="企业Logo" :span="2">
          <div v-if="editing" class="edit-field">
            <el-input v-model="form.logo_url" placeholder="请输入Logo URL" />
          </div>
          <el-image
            v-else-if="enterprise.logo_url"
            :src="enterprise.logo_url"
            style="width: 60px; height: 60px"
            fit="cover"
          />
          <span v-else>未设置</span>
        </el-descriptions-item>
        <el-descriptions-item label="企业简介" :span="2">
          <div v-if="editing" class="edit-field">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              placeholder="请输入企业简介"
            />
          </div>
          <span v-else>{{ enterprise.description || '暂无简介' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="企业标签" :span="2">
          <div v-if="editing" class="edit-field">
            <el-select
              v-model="form.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入标签后回车"
              style="width: 100%"
            >
              <el-option
                v-for="tag in enterprise.tags || []"
                :key="tag"
                :label="tag"
                :value="tag"
              />
            </el-select>
          </div>
          <div v-else>
            <el-tag
              v-for="tag in (enterprise.tags || [])"
              :key="tag"
              style="margin-right: 6px"
              size="small"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!enterprise.tags || enterprise.tags.length === 0">暂无标签</span>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyEnterprise, updateMyEnterprise } from '../../api/entAdmin'

const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const enterprise = ref(null)
const form = ref({
  description: '',
  logo_url: '',
  tags: [],
})

const authStatusMap = {
  verified: { label: '已认证', type: 'success' },
  pending: { label: '审核中', type: 'warning' },
  rejected: { label: '已拒绝', type: 'danger' },
  unclaimed: { label: '未认领', type: 'info' },
}

const authStatusType = computed(() => {
  return authStatusMap[enterprise.value?.auth_status]?.type || 'info'
})

const authStatusLabel = computed(() => {
  return authStatusMap[enterprise.value?.auth_status]?.label || enterprise.value?.auth_status || '-'
})

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getMyEnterprise()
    if (res.code === 200) {
      enterprise.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载企业信息失败')
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editing.value = true
  form.value = {
    description: enterprise.value?.description || '',
    logo_url: enterprise.value?.logo_url || '',
    tags: enterprise.value?.tags ? [...enterprise.value.tags] : [],
  }
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    const { data: res } = await updateMyEnterprise(form.value)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      editing.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.enterprise-info {
  max-width: 900px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.edit-field {
  width: 100%;
}
</style>
