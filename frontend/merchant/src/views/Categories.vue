<template>
  <div class="categories-view">
    <el-card>
      <div class="page-header">
        <h2>分类管理</h2>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加分类
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="categoryList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="sort_order" label="排序" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '添加分类'"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="categoryForm.name"
            placeholder="请输入分类名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="categoryForm.sort_order"
            :min="0"
            :max="9999"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
          <span class="form-tip">数值越小越靠前</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMyCategories, createCategory, updateCategory, deleteCategory } from '@/api/merchants'

const loading = ref(false)
const submitting = ref(false)
const categoryList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const categoryFormRef = ref(null)

const categoryForm = reactive({
  id: null,
  name: '',
  sort_order: 0
})

const categoryRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在1到50个字符', trigger: 'blur' }
  ]
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function fetchCategoryList() {
  loading.value = true
  try {
    categoryList.value = await getMyCategories()
  } catch (error) {
    console.error('获取分类列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(categoryForm, {
    id: row.id,
    name: row.name,
    sort_order: row.sort_order
  })
  dialogVisible.value = true
}

function handleDialogClose() {
  categoryFormRef.value?.resetFields()
  resetForm()
}

function resetForm() {
  categoryForm.id = null
  categoryForm.name = ''
  categoryForm.sort_order = 0
}

async function handleSubmit() {
  try {
    await categoryFormRef.value.validate()
    submitting.value = true
    const data = { ...categoryForm }

    if (isEdit.value) {
      await updateCategory(data.id, data)
      ElMessage.success('分类更新成功')
    } else {
      await createCategory(data)
      ElMessage.success('分类添加成功')
    }
    dialogVisible.value = false
    fetchCategoryList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${row.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    await deleteCategory(row.id)
    ElMessage.success('分类删除成功')
    fetchCategoryList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  fetchCategoryList()
})
</script>

<style scoped>
.categories-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.table-card {
  margin-top: 20px;
}

.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
