import { createWebHistory, createRouter } from "vue-router";
import LoginPage from "./components/LoginPage.vue";
import RegisterPage from "./components/RegisterPage.vue";

const routes = [
  {
    path: "/login",
    name: "LoginPage",
    component: LoginPage
  },
  {
    path: "/register",
    name: "RegisterPage",
    component: RegisterPage
  }
  

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;