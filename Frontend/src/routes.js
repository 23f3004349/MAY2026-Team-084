import { createWebHistory, createRouter } from "vue-router";
import HomePage from "./components/Home.vue";
import LoginPage from "./components/LoginPage.vue";
import RegisterPage from "./components/RegisterPage.vue";
import AssociationManager from "./components/AssociationManager.vue";
import AddAnnouncement from "./components/AddAnnouncement.vue";

const routes = [
  {
    path: "/",
    name: "HomePage",
    component: HomePage
  },
  {
    path: "/login",
    name: "LoginPage",
    component: LoginPage
  },
  {
    path: "/register",
    name: "RegisterPage",
    component: RegisterPage
  },
  {
    path: "/associate_manager",
    redirect: "/association_manager"
  },
  {
    path: "/admin_dashboard",
    redirect: "/association_manager"
  },
  {
    path: "/association_manager",
    name: "AssociationManager",
    component: AssociationManager
  }
  ,
  {
    path: "/add-announcement",
    name: "AddAnnouncement",
    component: AddAnnouncement
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;