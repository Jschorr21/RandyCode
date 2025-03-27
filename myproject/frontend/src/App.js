import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Navbar from "./components/Navbar";

function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem("access"));
  const [registerEmail, setRegisterEmail] = useState(null);
  const navigate = useNavigate();

  return (
    <>
      {isAuthenticated && <Navbar setIsAuthenticated={setIsAuthenticated} />}
      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/chat" /> : <Navigate to="/login" />}
        />
        <Route
          path="/login"
          element={
            <Login
              onLogin={() => setIsAuthenticated(true)}
              goToRegister={(email) => {
                setRegisterEmail(email);
                navigate("/register");
              }}
            />
          }
        />
        <Route
          path="/register"
          element={
            <Register
              email={registerEmail}
              onRegister={() => {
                setRegisterEmail(null);
                setIsAuthenticated(false);
              }}
            />
          }
        />
        <Route
          path="/chat"
          element={
            isAuthenticated ? <Chat /> : <Navigate to="/login" />
          }
        />
      </Routes>
    </>
  );
}

export default AppWrapper;
