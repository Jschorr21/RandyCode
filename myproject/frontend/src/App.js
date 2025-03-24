import { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem("access_token"));
  const [registerEmail, setRegisterEmail] = useState(null);

  return (
    <div>
      {isAuthenticated ? (
        <Chat />
      ) : registerEmail ? (
        <Register onRegister={() => setRegisterEmail(null)} />
      ) : (
        <Login
          onLogin={() => setIsAuthenticated(true)}
          goToRegister={(email) => setRegisterEmail(email)}
        />
      )}
    </div>
  );
}

export default App;
