<template>
  <div class="products-view">
    <el-card>
      <div class="page-header">
        <h2>商品管理</h2>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>
      </div>

      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索商品名称"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="searchForm.category_id"
          placeholder="分类筛选"
          clearable
          style="width: 150px"
        >
          <el-option
            v-for="cat in categoryList"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>

        <el-select
          v-model="searchForm.is_available"
          placeholder="上架状态"
          clearable
          style="width: 130px"
        >
          <el-option label="已上架" :value="true" />
          <el-option label="已下架" :value="false" />
        </el-select>

        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="productList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="商品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category_id" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryName(row.category_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            <span class="price">¥{{ formatMoney(row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="original_price" label="原价" width="100">
          <template #default="{ row }">
            <span v-if="row.original_price" class="original-price">¥{{ formatMoney(row.original_price) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" align="center">
          <template #default="{ row }">
            {{ row.stock === 0 ? '不限' : row.stock }}
          </template>
        </el-table-column>
        <el-table-column prop="is_available" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'info'" size="small">
              {{ row.is_available ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              :type="row.is_available ? 'warning' : 'success'"
              @click="handleToggle(row)"
            >
              {{ row.is_available ? '下架' : '上架' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑商品' : '添加商品'"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="100px"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" maxlength="100" />
        </el-form-item>

        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="productForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="cat in categoryList"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
            maxlength="500"
          />
        </el-form-item>

        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="productForm.price"
            :min="0.01"
            :max="99999.99"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="原价">
          <el-input-number
            v-model="productForm.original_price"
            :min="0.01"
            :max="99999.99"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="库存">
          <el-input-number
            v-model="productForm.stock"
            :min="0"
            :max="999999"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
          <span class="form-tip">0表示不限库存</span>
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number
            v-model="productForm.sort_order"
            :min="0"
            :max="9999"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="商品主图">
          <div class="image-upload-container">
            <el-upload
              class="image-uploader"
              action=""
              :show-file-list="false"
              :on-change="handleMainImageChange"
              :before-upload="beforeImageUpload"
              :disabled="submitting"
            >
              <img v-if="productForm.image_url" :src="getImageUrl(productForm.image_url)" class="uploaded-image" />
              <el-icon v-else class="uploader-icon"><Picture /></el-icon>
            </el-upload>
            <div class="upload-tips">
              <span class="tip-text">支持 jpg、png、gif、webp 格式，最大10MB</span>
              <el-button
                v-if="productForm.image_url"
                type="danger"
                size="small"
                text
                @click="productForm.image_url = ''"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="多张图片">
          <div class="multi-image-section">
            <div class="multi-image-list">
              <div v-for="(img, index) in productForm.multiImages" :key="index" class="multi-image-item">
                <el-image
                  :src="getImageUrl(img.url)"
                  fit="cover"
                  class="multi-image-preview"
                  :preview-src-list="productForm.multiImages.map(i => getImageUrl(i.url))"
                />
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  circle
                  class="image-delete-btn"
                  @click="removeMultiImage(index)"
                />
              </div>
              <el-upload
                v-if="productForm.multiImages.length < 9"
                class="simple-uploader"
                action=""
                :show-file-list="false"
                :on-change="handleMultiImageAdd"
                :before-upload="beforeImageUpload"
                :disabled="submitting"
              >
                <div class="upload-trigger">
                  <el-icon :size="30"><Plus /></el-icon>
                  <span class="upload-text">上传</span>
                </div>
              </el-upload>
            </div>
            <div class="upload-tips">
              <span class="tip-text">最多上传9张商品图片，jpg、png、gif、webp 格式，单张最大10MB</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="上架状态">
          <el-switch
            v-model="productForm.is_available"
            active-text="上架"
            inactive-text="下架"
          />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Upload, Delete, Picture } from '@element-plus/icons-vue'
import { getMyProducts, createProduct, updateProduct, deleteProduct, toggleProduct } from '@/api/products'
import { getMyCategories } from '@/api/merchants'
import { uploadProductImage } from '@/api/upload'

const loading = ref(false)
const submitting = ref(false)
const productList = ref([])
const categoryList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const productFormRef = ref(null)

const searchForm = reactive({
  keyword: '',
  category_id: '',
  is_available: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const productForm = reactive({
  id: null,
  name: '',
  category_id: null,
  description: '',
  price: 0,
  original_price: null,
  stock: 0,
  sort_order: 0,
  image_url: '',
  multiImages: [],
  is_available: true
})

const uploading = ref(false)

const productRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 1, max: 100, message: '商品名称长度在1到100个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择所属分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' }
  ]
}

function formatMoney(value) {
  if (!value && value !== 0) return '0.00'
  return Number(value).toFixed(2)
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

function getCategoryName(categoryId) {
  const category = categoryList.value.find(c => c.id === categoryId)
  return category ? category.name : '-'
}

async function fetchProductList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.category_id) {
      params.category_id = searchForm.category_id
    }
    if (searchForm.is_available !== '') {
      params.is_available = searchForm.is_available
    }
    const data = await getMyProducts(params)
    productList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取商品列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchCategoryList() {
  try {
    categoryList.value = await getMyCategories()
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

function handleSearch() {
  pagination.page = 1
  fetchProductList()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.category_id = ''
  searchForm.is_available = ''
  pagination.page = 1
  fetchProductList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchProductList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchProductList()
}

function handleAdd() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  let multiImages = []
  if (row.images) {
    try {
      const parsed = typeof row.images === 'string' ? JSON.parse(row.images) : row.images
      if (Array.isArray(parsed)) {
        multiImages = parsed.map(url => ({ url, name: '' }))
      }
    } catch (e) {
      const urls = row.images.split(',').filter(u => u.trim())
      multiImages = urls.map(url => ({ url, name: '' }))
    }
  }
  Object.assign(productForm, {
    id: row.id,
    name: row.name,
    category_id: row.category_id,
    description: row.description || '',
    price: row.price,
    original_price: row.original_price || null,
    stock: row.stock,
    sort_order: row.sort_order,
    image_url: row.image_url || '',
    multiImages: multiImages,
    is_available: row.is_available
  })
  dialogVisible.value = true
}

function handleDialogClose() {
  productFormRef.value?.resetFields()
  resetForm()
}

function resetForm() {
  productForm.id = null
  productForm.name = ''
  productForm.category_id = null
  productForm.description = ''
  productForm.price = 0
  productForm.original_price = null
  productForm.stock = 0
  productForm.sort_order = 0
  productForm.image_url = ''
  productForm.multiImages = []
  productForm.is_available = true
}

function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return url
}

function beforeImageUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return false
}

async function handleMainImageChange(file) {
  if (uploading.value) return
  try {
    uploading.value = true
    const response = await uploadProductImage(file.raw)
    productForm.image_url = response.data.url
    ElMessage.success('主图上传成功')
  } catch (error) {
    console.error('主图上传失败:', error)
  } finally {
    uploading.value = false
  }
}

async function handleMultiImageAdd(file) {
  if (uploading.value) return
  if (productForm.multiImages.length >= 9) {
    ElMessage.warning('最多只能上传9张图片')
    return
  }
  try {
    uploading.value = true
    const response = await uploadProductImage(file.raw)
    productForm.multiImages.push({
      url: response.data.url,
      name: response.data.filename
    })
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('图片上传失败:', error)
  } finally {
    uploading.value = false
  }
}

function removeMultiImage(index) {
  productForm.multiImages.splice(index, 1)
}

async function handleSubmit() {
  try {
    await productFormRef.value.validate()
    submitting.value = true
    const data = { ...productForm }
    if (!data.original_price) delete data.original_price
    data.images = JSON.stringify(data.multiImages.map(img => img.url))
    delete data.multiImages

    if (isEdit.value) {
      await updateProduct(data.id, data)
      ElMessage.success('商品更新成功')
    } else {
      await createProduct(data)
      ElMessage.success('商品添加成功')
    }
    dialogVisible.value = false
    fetchProductList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleToggle(row) {
  try {
    const action = row.is_available ? '下架' : '上架'
    await ElMessageBox.confirm(`确定要${action}该商品吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await toggleProduct(row.id)
    ElMessage.success(`商品${action}成功`)
    fetchProductList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除商品"${row.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    await deleteProduct(row.id)
    ElMessage.success('商品删除成功')
    fetchProductList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  fetchProductList()
  fetchCategoryList()
})
</script>

<style scoped>
.products-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.search-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.table-card {
  margin-top: 20px;
}

.price {
  color: #f56c6c;
  font-weight: 600;
}

.original-price {
  color: #909399;
  text-decoration: line-through;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-uploader {
  width: 160px;
  height: 160px;
}

.image-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.image-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.uploader-icon {
  font-size: 48px;
  color: #8c939d;
  width: 160px;
  height: 160px;
  text-align: center;
  line-height: 160px;
}

.uploaded-image {
  width: 160px;
  height: 160px;
  display: block;
  object-fit: cover;
}

.upload-tips {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 8px;
}

.multi-image-section {
  width: 100%;
}

.multi-image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.multi-image-item {
  position: relative;
  width: 100px;
  height: 100px;
}

.multi-image-preview {
  width: 100px;
  height: 100px;
  border-radius: 6px;
  overflow: hidden;
}

.multi-image-preview :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
}

.simple-uploader {
  width: 100px;
  height: 100px;
}

.simple-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.simple-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #8c939d;
}

.upload-text {
  font-size: 12px;
  color: #8c939d;
}
</style>
