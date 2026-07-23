import { createWebHistory, createRouter } from "vue-router";

import HomePage from "./components/Home.vue";
import LoginPage from "./components/LoginPage.vue";
import RegisterPage from "./components/RegisterPage.vue";
import AssociationManager from "./components/AssociationManager.vue";
import AddAnnouncement from "./components/AddAnnouncement.vue";
import EditAnnouncement from "./components/EditAnnouncement.vue";
import Members from "./components/Members.vue";
import AddMember from "./components/AddMember.vue";
import EditMember from "./components/EditMember.vue";
import Associationcomplaint from "./components/Associationcomplaint.vue";
import ComplaintDetail from "./components/ComplaintDetail.vue";
import AddComplaint from "./components/AddComplaint.vue";
import AssociationInvoice from "./components/AssociationInvoice.vue";
import InvoiceDetail from "./components/InvoiceDetail.vue";
import TenantDashboard from "./components/TenantDashboard.vue";
import TenantComplaint from "./components/TenantComplaint.vue";
import TenantComplaintDetails from "./components/TenantComplaintDetails.vue";
import RaiseComplaint from "./components/AddComplaint.vue";

const routes = [
  { path: "/", component: HomePage },
  { path: "/login", component: LoginPage },
  { path: "/register", component: RegisterPage },

  { path: "/associate_manager", redirect: "/association_manager" },
  { path: "/admin_dashboard", redirect: "/association_manager" },

  { path: "/association_manager", component: AssociationManager },
  { path: "/add-announcement", component: AddAnnouncement },
  { path: "/edit-announcement/:id", component: EditAnnouncement, props: true },

  { path: "/members", component: Members },
  { path: "/add-member", component: AddMember },
  { path: "/edit-member/:id", component: EditMember, props: true },

  { path: "/complaints", component: Associationcomplaint },
  { path: "/complaints/:id", component: ComplaintDetail, props: true },
  { path: "/add-complaint", component: AddComplaint },

  { path: "/invoices", component: AssociationInvoice },
  { path: "/invoices/:id/detail", component: InvoiceDetail, props: true },

  { path: "/tenant-dashboard", component: TenantDashboard },
  { path: "/tenant-complaints", component: TenantComplaint },
  {
    path: "/tenant-complaints/:id",
    component: TenantComplaintDetails,
    props: true,
  },
  { path: "/raise-complaint", component: RaiseComplaint },

  { path: "/Tenant_dashboard", redirect: "/tenant-dashboard" },
  { path: "/tenant_dashboard", redirect: "/tenant-dashboard" },
  { path: "/Tenant_complaints", redirect: "/tenant-complaints" },

  { path: "/payments", redirect: "/tenant-dashboard" },
  { path: "/info", redirect: "/tenant-dashboard" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  // Allow public pages
  if (to.path === "/" || to.path === "/login" || to.path === "/register") {
    return next();
  }

  // Require login
  if (!token) {
    return next("/login");
  }

  // Admin pages
  if (
    to.path.startsWith("/association_manager") ||
    to.path.startsWith("/members") ||
    to.path.startsWith("/add-member") ||
    to.path.startsWith("/edit-member") ||
    to.path.startsWith("/add-announcement") ||
    to.path.startsWith("/edit-announcement") ||
    to.path === "/complaints" ||
    to.path.startsWith("/invoices")
  ) {
    if (role !== "ADMIN" && role !== "SYSTEM_ADMIN") {
      return next("/tenant-dashboard");
    }
  }

  // Tenant pages
  if (
    to.path.startsWith("/tenant-dashboard") ||
    to.path.startsWith("/tenant-complaints") ||
    to.path.startsWith("/raise-complaint")
  ) {
    if (role !== "TENANT" && role !== "OWNER") {
      return next("/association_manager");
    }
  }

  next();
});

export default router;
