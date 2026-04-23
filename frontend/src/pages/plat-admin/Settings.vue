<template>
  <div class="settings-page">
    <!-- 基础设置 -->
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基础设置</span>
          <el-button v-if="!editing" type="primary" @click="startEdit">编辑</el-button>
          <div v-else class="edit-actions">
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="平台名称">
          <template v-if="editing">
            <el-input v-model="form.platform_name" />
          </template>
          <template v-else>{{ settings.platform_name || '-' }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="客服热线">
          <template v-if="editing">
            <el-input v-model="form.support_phone" />
          </template>
          <template v-else>{{ settings.support_phone || '-' }}</template>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 安全与策略（预留） -->
    <el-card class="section-card">
      <template #header>
        <span>安全与策略</span>
      </template>
      <el-empty description="功能开发中，敬请期待" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../../api/platAdmin'

const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const settings = ref({})
const form = ref({})

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getSettings()
    if (res.code === 200) {
      settings.value = res.data.items || res.data || {}
    }
  } catch {
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editing.value = true
  form.value = {
    platform_name: settings.value.platform_name || '',
    support_phone: settings.value.support_phone || '',
  }
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    const keys = Object.keys(form.value)
    for (const key of keys) {
      const { data: res } = await updateSettings({ key, value: form.value[key] })
      if (res.code !== 200) {
        ElMessage.error(res.message || '保存失败')
        return
      }
    }
    ElMessage.success('保存成功')
    editing.value = false
    await fetchData()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
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

.edit-actions {
  display: flex;
  gap: 8px;
}

.section-card {
  margin-top: 16px;
}
</style>
