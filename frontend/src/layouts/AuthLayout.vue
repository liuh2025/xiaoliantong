<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-brand">
        <h1 class="auth-logo">校链通</h1>
        <p class="auth-slogan">校友企业 互联互通</p>
      </div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-brand {
  text-align: center;
  margin-bottom: 32px;
  color: #fff;
}

.auth-logo {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.auth-slogan {
  font-size: 1rem;
  opacity: 0.9;
}
</style>
