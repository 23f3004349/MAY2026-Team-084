<template>
   <div class="content-wrapper">
      <!-- Navigation Header -->
      <nav class="navbar">
         <div class="nav-container">
            <!-- Logo on left -->
            <div class="logo-section">
               <div class="logo"> SocietyEase</div>
            </div>

            <!-- Auth buttons on right -->
            <div class="nav-buttons">
               <button @click="$router.push('/login')" class="nav-btn btn-login">
                  Login
               </button>
               <button @click="$router.push('/register')" class="nav-btn btn-signup">
                  Sign up
               </button>
            </div>
         </div>
      </nav>

      <!-- Hero Section with Logo and Description -->
      <section class="hero-section">
         <div class="hero-content">
            <div class="hero-logo"></div>
            <h1 class="hero-title">Welcome to SocietyEase</h1>
            <p class="hero-subtitle">Community Services Platform</p>

            <!-- Description replacing search bar -->
            <div class="description-box">
              <p class="desc-main">Connect with your community, access local resources, and stay informed about neighborhood events and initiatives.</p>
              <p class="desc-secondary">Manage notices, polls, parking, maintenance requests and community members — all in one simple, secure platform built for societies.</p>
            </div>

            <!-- CTA Button -->
            <div class="cta-section">
               <button @click="$router.push('/login')" class="cta-btn">
                  Get Started ⮕
               </button>
            </div>
         </div>
      </section>
   </div>
</template>

<script>
import axios from 'axios';

export default {
   name: 'Content',
   data() {
      return {
         stats: {
            departments: 0,
            doctors: 0,
            patients: 0
         }
      }
   },
   mounted() {
      this.fetchStats();
   },
   methods: {
      async fetchStats() {
         try {
            const token = localStorage.getItem('access_token');
            if (!token) {
               // If no token, show default stats
               this.stats = { departments: 0, doctors: 0, patients: 0 };
               return;
            }

            const headers = { Authorization: `Bearer ${token}` };

            // Fetch departments
            const deptRes = await axios.get('http://127.0.0.1:5000/api/departments', { headers });
            this.stats.departments = deptRes.data.length;

            // Fetch doctors
            const docRes = await axios.get('http://127.0.0.1:5000/api/admin/doctors', { headers });
            this.stats.doctors = docRes.data.length;

            // Fetch patients
            const patRes = await axios.get('http://127.0.0.1:5000/api/admin/patients', { headers });
            this.stats.patients = patRes.data.length;
         } catch (error) {
            console.error('Error fetching statistics:', error);
            // Keep default values on error
         }
      }
   }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 1.5rem 0 2rem;
  background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%);
  color: #000000;
}

.navbar {
  background: #ffffff;
  border-bottom: 1px solid rgba(135, 172, 210, 0.12);
  padding: 1rem 0;
  box-shadow: 0 10px 30px rgba(132, 170, 210, 0.04);
}

.nav-container {
   max-width: 1400px;
   margin: 0 auto;
   padding: 0 2rem;
   display: flex;
   justify-content: space-between;
   align-items: center;
}

.logo {
   font-size: 1.8rem;
   font-weight: 900;
   color: #000000;
   cursor: pointer;
   transition: color 0.3s ease;
   letter-spacing: -0.02em;
   margin-right: 1rem;
}


.nav-buttons {
   display: flex;
   gap: 1rem;
   align-items: center;
}

.nav-btn {
   padding: 0.6rem 1.2rem;
   border-radius: 8px;
   font-size: 0.95rem;
   font-weight: 700;
   cursor: pointer;
   transition: all 0.2s ease;
   white-space: nowrap;
}
.btn-login {
   background: #ffffff;
   color: #000000;
   border: 1px solid rgba(0,0,0,0.08);
}
.btn-login:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.06); }
.btn-signup {
   background: linear-gradient(135deg,#5c92df 0%, #84b5f1 100%);
   color: #ffffff;
   border: none;
}
.btn-signup:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(92,146,223,0.18); }

/* Hero uses the left-panel styling from LoginPage for a cohesive look */
.hero-section {
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  padding: 2.2rem 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #264863;
  position: relative;
  overflow: hidden;
  max-width: 1200px;
  margin: 1.5rem auto 2rem;
  border-radius: 2rem;
  text-align: center;
}

.hero-content { position: relative; z-index:2; animation: slideInLeft 0.8s ease-out; max-width:700px; }
@keyframes slideInLeft { from { opacity:0; transform:translateX(-30px);} to { opacity:1; transform:translateX(0);} }

.hero-title {
  font-size: clamp(2rem, 2.8vw, 2.6rem);
  font-weight: 800;
  margin-bottom: 0.6rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: #000000;
}

.hero-subtitle {
  font-size: clamp(1.05rem, 1.4vw, 1.25rem);
  margin-bottom: 1rem;
  opacity: 0.95;
  font-weight: 700;
  color: #000000;
}

.description-box {
  background: #ffffff;
  padding: 1.8rem;
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.06);
  margin-bottom: 1.5rem;
  border: 1px solid rgba(34,49,63,0.04);
}

.desc-main { font-size: 1rem; color:#1f3346; font-weight:700; margin-bottom:0.6rem; line-height:1.6; }
.desc-secondary { font-size:0.95rem; color:#3b556e; line-height:1.6; margin:0; }

.cta-section { margin-top:0.8rem }
.cta-btn { padding:0.9rem 2rem; font-size:1rem; font-weight:800; color:#fff; background:linear-gradient(135deg,#5c92df 0%, #84b5f1 100%); border:none; border-radius:999px; cursor:pointer; box-shadow:0 8px 20px rgba(92,146,223,0.12); }
.cta-btn:hover { transform:translateY(-2px); }

@media (max-width: 992px) {
  .hero-section { margin: 1rem; padding:1.6rem; }
  .hero-title { font-size: 2rem; }
  .hero-subtitle { font-size: 1rem; }
}

@media (max-width: 480px) {
  .nav-buttons { gap:0.5rem; }
  .hero-title { font-size:1.5rem; }
  .desc-main { font-size:0.95rem; }
  .desc-secondary { font-size:0.85rem; }
}
</style>
