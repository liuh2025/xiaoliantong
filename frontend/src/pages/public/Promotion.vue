<template>
  <div class="promotion-page">
    <!-- Hero -->
    <section class="promo-hero">
      <h1 class="promo-title">校链通</h1>
      <p class="promo-subtitle">校友企业互联互通平台</p>
      <p class="promo-desc">
        汇聚校友资源，连接企业商机，打造校友企业生态圈。
        无论您是企业主还是校友，校链通帮您发现更多合作可能。
      </p>
    </section>

    <!-- Features -->
    <section class="promo-features">
      <div class="feature-card">
        <div class="feature-icon">&#127970;</div>
        <h3>企业名录</h3>
        <p>浏览校友企业，按行业、地区精准查找，建立商务联系</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">&#128188;</div>
        <h3>商机广场</h3>
        <p>发布采购和供应信息，快速对接校友企业资源</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">&#128172;</div>
        <h3>校友圈</h3>
        <p>分享行业动态和经验，保持校友间的紧密联系</p>
      </div>
    </section>

    <!-- Download Section -->
    <section class="promo-download">
      <h2 class="download-title">立即加入</h2>
      <p class="download-desc">扫描二维码或点击链接下载校链通</p>
      <div class="download-content">
        <div class="qr-placeholder">
          <div class="qr-box">
            <span>二维码占位</span>
          </div>
          <p>微信扫码</p>
        </div>
        <div class="download-links">
          <el-button type="primary" size="large" disabled>
            iOS 下载（即将上线）
          </el-button>
          <el-button size="large" disabled>
            Android 下载（即将上线）
          </el-button>
          <el-button size="large" @click="$router.push('/')">
            网页版体验
          </el-button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <section class="promo-footer">
      <p>&copy; 2026 校链通 XiaoLianTong. All rights reserved.</p>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.promotion-page {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: var(--spacing-2xl);
}

.promo-hero {
  text-align: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-xl);
}

.promo-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.promo-subtitle {
  font-size: var(--font-size-xl);
  opacity: 0.9;
  margin-bottom: var(--spacing-md);
}

.promo-desc {
  font-size: var(--font-size-base);
  opacity: 0.85;
  line-height: 1.6;
  max-width: 500px;
  margin: 0 auto;
}

.promo-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.feature-card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: var(--spacing-sm);
}

.feature-card h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

.feature-card p {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.promo-download {
  text-align: center;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--spacing-xl);
}

.download-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.download-desc {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.download-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2xl);
}

.qr-placeholder {
  text-align: center;
}

.qr-box {
  width: 160px;
  height: 160px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-placeholder);
  font-size: var(--font-size-sm);
}

.qr-placeholder p {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.download-links {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.promo-footer {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--color-text-placeholder);
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .promo-features {
    grid-template-columns: 1fr;
  }
  .download-content {
    flex-direction: column;
  }
}
</style>
