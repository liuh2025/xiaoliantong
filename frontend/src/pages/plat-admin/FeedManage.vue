<template>
  <div class="feed-manage-page">
    <el-card>
      <template #header>
        <span>动态内容管理</span>
      </template>

      <!-- Filter -->
      <div class="filter-bar">
        <el-input
          v-model="searchKey"
          placeholder="搜索动态内容"
          clearable
          style="width: 240px"
          @clear="fetchData"
          @keyup.enter="fetchData"
        />
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px" @change="fetchData">
          <el-option label="正常" value="active" />
          <el-option label="已下线" value="offline" />
        </el-select>
        <el-button type="primary" @click="fetchData">搜索</el-button>
      </div>

      <el-table :data="list" v-loading="loading" empty-text="暂无动态数据">
        <el-table-column prop="content" label="内容" min-width="280" show-overflow-tooltip />
        <el-table-column prop="publisher_name" label="发布人" min-width="100" />
        <el-table-column prop="enterprise_name" label="所属企业" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '正常' : '已下线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" min-width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetailDialog(row)">查看详情</el-button>
            <el-button
              v-if="row.status === 'active'"
              size="small"
              type="danger"
              @click="openOfflineDialog(row)"
            >下线</el-button>
            <span v-else class="text-secondary">已处理</span>
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

    <!-- Offline Dialog -->
    <el-dialog v-model="offlineVisible" title="下线动态" width="480px" destroy-on-close>
      <el-form :model="offlineForm" label-width="80px">
        <el-form-item label="动态内容">
          <span class="content-preview">{{ currentRow?.content }}</span>
        </el-form-item>
        <el-form-item label="下线原因" required>
          <el-input v-model="offlineForm.reason" type="textarea" :rows="3" placeholder="请填写下线原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="offlineVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="submitOffline">确认下线</el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="动态详情" width="600px" destroy-on-close>
      <div v-loading="detailLoading">
        <el-descriptions v-if="detailRow" :column="1" border>
          <el-descriptions-item label="发布人">{{ detailRow.publisher_name }}</el-descriptions-item>
          <el-descriptions-item label="所属企业">{{ detailRow.enterprise_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailRow.status === 'active' ? 'success' : 'info'" size="small">
              {{ detailRow.status === 'active' ? '正常' : '已下线' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发布时间">{{ detailRow.created_at }}</el-descriptions-item>
          <el-descriptions-item label="动态内容">
            <div style="white-space:pre-wrap;line-height:1.6;">{{ detailRow.content }}</div>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailRow.images && detailRow.images.length" label="图片">
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              <img v-for="(img, idx) in detailRow.images" :key="idx" :src="img" style="width:80px;height:80px;object-fit:cover;border-radius:4px;" />
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getContentFeeds, getContentFeedDetail, offlineContentFeed } from '../../api/platAdmin'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKey = ref('')
const filterStatus = ref('')

const offlineVisible = ref(false)
const submitting = ref(false)
const currentRow = ref(null)
const offlineForm = ref({ reason: '' })

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailRow = ref(null)

async function openDetailDialog(row) {
  detailRow.value = null
  detailVisible.value = true
  detailLoading.value = true
  try {
    const { data: res } = await getContentFeedDetail(row.id)
    if (res.code === 200) {
      detailRow.value = res.data
    } else {
      detailRow.value = row
    }
  } catch {
    detailRow.value = row
  } finally {
    detailLoading.value = false
  }
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchKey.value) params.keyword = searchKey.value
    if (filterStatus.value) params.status = filterStatus.value
    const { data: res } = await getContentFeeds(params)
    if (res.code === 200) {
      list.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载动态列表失败')
  } finally {
    loading.value = false
  }
}

function openOfflineDialog(row) {
  currentRow.value = row
  offlineForm.value = { reason: '' }
  offlineVisible.value = true
}

async function submitOffline() {
  if (!offlineForm.value.reason) {
    ElMessage.warning('请填写下线原因')
    return
  }
  submitting.value = true
  try {
    const { data: res } = await offlineContentFeed(currentRow.value.id, { reason: offlineForm.value.reason })
    if (res.code === 200) {
      ElMessage.success('已下线')
      offlineVisible.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.content-preview {
  max-height: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.text-secondary {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style>
