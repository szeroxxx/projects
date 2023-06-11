import Register from "./components/Register/Register";
import Login from "./components/Login/Login";
import ResetPassword from "./components/Login/ResetPassword";
import Home from "./components/Home";
import AppLayout from "./components/AppLayout";
import Admin from "./components/Admin";
import Missing from "./components/Missing";
import Unauthorized from "./components/Unauthorized";
import Settings from "./components/Settings/Settings";
import RequireAuth from "./components/RequireAuth";
import PersistLogin from "./components/PersistLogin";
import { Routes, Route } from "react-router-dom";
import Customers from "./components/Customers/Customers";
import CustomerNew from "./components/Customers/CustomerNew";
import Dashboard from "./components/Dashboard/Dashboard";
import Projects from "./components/Projects/Projects";
import Invitations from "./components/Settings/Team/Invitation";
import Project from "./components/Projects/Project/Project";
import Customer from "./components/Customers/Customer/Customer";
function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        {/* public routes */}
        <Route path="login" element={<Login />} />
        <Route path="password_reset" element={<ResetPassword />} />
        <Route path="register" element={<Register />} />
        <Route path="unauthorized" element={<Unauthorized />} />
        <Route path="/invitation" element={<Invitations />} />
        {/* we want to protect these routes */}
        <Route element={<PersistLogin />}>
          <Route element={<RequireAuth />}>
            <Route path="customers" element={<Customers />} />
            <Route path="customers/:customer_id" element={<CustomerNew />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="/" element={<Home />} />
            <Route path="admin" element={<Admin />} />
            <Route path="settings" element={<Settings />} />
            <Route path="/project/:project_id" element={<Project />} />
            <Route path="/customer/:customer_id" element={<Customer />} />
          </Route>
        </Route>
        {/* catch all */}
        <Route path="*" element={<Missing />} />
      </Route>
    </Routes>
  );
}

export default App;
