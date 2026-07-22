<template>
  <div class="login-wrapper min-vh-100">
    <nav class="navbar-top navbar-expand-lg">
      <div class="navbar-container container-fluid">
        <div class="logo-section">
          <span class="logo">SocietyEase</span>
        </div>
        <div class="nav-info">
          <span class="nav-text">Don't have an account? <router-link to="/register" class="signup-link">Sign Up</router-link></span>
        </div>
      </div>
    </nav>

    <div class="login-container">
      <div class="left-section">
        <div class="background-content">
          <div class="content-overlay">
            <h1 class="left-title">Welcome to SocietyEase</h1>
            <p class="left-subtitle">Community Services Platform</p>
            <p class="left-description">Connect with your community, access resources, and stay informed about local events and initiatives.</p>
          </div>
        </div>
      </div>

      <div class="right-section">
        <div class="form-container card border-0 shadow-sm">
          <div class="card-body p-4 p-md-5">
            <h2 class="form-title">Sign in to SocietyEase</h2>
            <p class="form-subtitle">Enter your credentials to access your account</p>

            <div class="social-login">
              <button class="social-btn google-btn btn" @click="handleGoogleLogin">
                <span class="google-icon"></span>
                <span>Sign in with Google</span>
              </button>
              <button class="social-btn microsoft-btn btn" @click="handleMicrosoftLogin">
                <span class="microsoft-icon"></span>
                <span>Sign in with Microsoft</span>
              </button>
            </div>

            <div class="divider">
              <span>Or continue with email</span>
            </div>

            <form @submit.prevent="submit">
              <div class="form-group mb-3">
                <label for="username" class="form-label">Email Address</label>
                <input
                  id="username"
                  v-model="form.username"
                  type="email"
                  class="form-input form-control"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div class="form-group mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  id="password"
                  v-model="form.password"
                  type="password"
                  class="form-input form-control"
                  placeholder="Enter your password"
                  required
                />
              </div>

              <div v-if="error" class="alert alert-error">
                ✕ {{ error }}
              </div>

              <button type="submit" class="sign-in-btn btn w-100" :disabled="loading">
                {{ loading ? 'Signing in...' : 'Sign In' }}
              </button>
            </form>

            <p class="signup-prompt mt-4">
              Need a SocietyEase account?
              <router-link to="/register" class="signup-link-bottom">Sign Up</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getApiBase } from '../utils/auth'

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const router = useRouter()

function handleGoogleLogin() {
  alert('Google login integration coming soon! Backend authentication needed.')
}

function handleMicrosoftLogin() {
  alert('Microsoft login integration coming soon! Backend authentication needed.')
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const res = await axios.post(`${getApiBase()}/api/auth/login`, {
      email: form.value.username,
      password: form.value.password
    }, {
      headers: { 'Content-Type': 'application/json' }
    })

    if (res.data.token) {
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('role', res.data.user.role)
      
      const role = (res.data.user.role || '').toLowerCase()
      if (role === 'admin') router.push('/associate_manager')
      else router.push('/tenant-dashboard')
    } else {
      error.value = res.data.message || 'Login failed'
    }
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 1.5rem 0 2rem;
  background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%);
  color: #000000;
}

.navbar-top {
  background: #ffffff;
  border-bottom: 1px solid rgba(135, 172, 210, 0.2);
  padding: 1rem 0;
  box-shadow: 0 10px 30px rgba(132, 170, 210, 0.08);
}

.navbar-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 1.4rem;
  font-weight: 800;
  color: #000000;
  cursor: pointer;
  transition: color 0.3s ease;
  letter-spacing: -0.02em;
}

.logo:hover {
  color: #a68a72;
}

.nav-info {
  display: flex;
  align-items: center;
}

.nav-text {
  color: #000000;
  font-size: 0.95rem;
}

.signup-link {
  color:black;
  text-decoration: none;
  font-weight: 700;
  margin-left: 0.5rem;
  transition: color 0.3s ease;
}

.signup-link:hover {
  color:black;
  text-decoration: underline;
}

.login-container {
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 1.5rem auto 2rem;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 2rem;
  align-items: stretch;
  padding: 0 1rem;
}

.left-section {
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  padding: 2.2rem 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #264863;
  position: relative;
  overflow: hidden;
  max-width: 1000px;
  min-height: 520px;
  border-radius: 2rem;
}




.background-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.content-overlay {
  animation: slideInLeft 0.8s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.left-title {
  font-size: clamp(2rem, 2.8vw, 2.6rem);
  font-weight: 800;
  margin-bottom: 0.9rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: #000000;
}

.left-subtitle {
  font-size: clamp(1.05rem, 1.4vw, 1.25rem);
  margin-bottom: 1.35rem;
  opacity: 0.95;
  font-weight: 700;
  color: #000000;
}

.left-description {
  font-size: 1rem;
  opacity: 0.95;
  line-height: 1.6;
  max-width: 350px;
  color: #000000;
}

.right-section {
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.form-container {
  width: 100%;
  max-width: 520px;
  border-radius: 2rem;
  overflow: hidden;
  animation: slideInRight 0.8s ease-out;
}

.form-container .card-body {
  padding: 2rem 1.75rem;
  background: #ffffff;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.form-title {
  font-size: 1.8rem;
  color: #000000;
  margin-bottom: 0.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.form-subtitle {
  color: #000000;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.social-login {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.5rem;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(129, 167, 210, 0.2);
  border-radius: 1.25rem;
  background: #f8fbff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-weight: 700;
  color: #2f5f83;
}

.social-btn:hover {
  border-color: #8bb7e1;
  background: #eef6ff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(124, 165, 209, 0.15);
}

.google-icon,
.microsoft-icon {
  font-size: 1.2rem;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: #8aa7c4;
  font-size: 0.85rem;
  font-weight: 600;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(145, 175, 204, 0.25);
}

.divider::before {
  margin-right: 1rem;
}

.divider::after {
  margin-left: 1rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #000000;
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 0.3px;
}

.form-input {
  width: 100%;
  padding: 0.85rem 1.1rem;
  color: #000000;
  border: 2px solid #d7e5f5;
  border-radius: 16px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #fbfdff;
  font-weight: 500;
}

.form-input:hover {
  border-color: #b7d1ec;
}

.form-input:focus {
  outline: none;
  border-color: #aac9ed;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(170, 201, 237, 0.15);
}

.form-input::placeholder {
  color: #888888;
}

.forgot-password {
  text-align: right;
  margin-bottom: 1.5rem;
}

.forgot-link {
  color: #000000;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: color 0.3s ease;
}

.forgot-link:hover {
  color: #5f8db9;
  text-decoration: underline;
}

.alert {
  padding: 1rem 1.1rem;
  border-radius: 16px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  border: 2px solid rgba(209, 226, 242, 0.9);
}

.alert-error {
  background: #f8fbff;
  color: #356a93;
  border: 2px solid #c7ddef;
}

.sign-in-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #5c92df 0%, #84b5f1 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(92, 146, 223, 0.2);
  letter-spacing: 0.5px;
}

.sign-in-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(92, 146, 223, 0.28);
}

.sign-in-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sign-in-btn:active:not(:disabled) {
  transform: translateY(0);
}

.signup-prompt {
  text-align: center;
  margin-top: 1.75rem;
  color: #000000;
  font-size: 0.95rem;
  font-weight: 500;
}

.signup-link-bottom {
  color: #5c92df;
  font-weight: 700;
}

.signup-link-bottom {
  color: black;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.3s ease;
}

.signup-link-bottom:hover {
  color: black;
  text-decoration: underline;
}

@media (max-width: 992px) {
  .login-container {
    grid-template-columns: 1fr;
    margin: 1.5rem auto 2rem;
    gap: 1.5rem;
  }

  .left-section {
    display: none;
  }

  .right-section {
    padding: 0 1rem;
  }

  .form-container {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .nav-info {
    font-size: 0.85rem;
  }

  .right-section {
    padding: 1.5rem;
  }

  .form-title {
    font-size: 1.5rem;
  }

  .social-login {
    grid-template-columns: 1fr;
  }

  .social-btn {
    text-align: center;
  }

  .form-input {
    padding: 0.65rem 0.9rem;
  }
}

@media (max-width: 480px) {
  .navbar-top {
    padding: 0.75rem 0;
  }

  .navbar-container {
    padding: 0 1rem;
  }

  .logo {
    font-size: 1.2rem;
  }

  .nav-text {
    display: none;
  }

  .right-section {
    padding: 1rem;
  }

  .form-container {
    padding: 0;
  }

  .form-title {
    font-size: 1.3rem;
  }

  .form-subtitle {
    font-size: 0.85rem;
  }

  .left-title {
    font-size: 1.8rem;
  }

  .left-subtitle {
    font-size: 1.1rem;
  }
}
</style>