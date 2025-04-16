import { getExternalLogout } from "@/contexts/AuthContext";

const logout = getExternalLogout();
if (logout) logout();

export const fetchWithAuth = async (input: RequestInfo, init?: RequestInit) => {
    let access = localStorage.getItem("access");
  
    const res = await fetch(input, {
      ...init,
      headers: {
        ...init?.headers,
        Authorization: `Bearer ${access}`,
        "Content-Type": "application/json",
      },
    });
  
    if (res.status === 401) {
      const refresh = localStorage.getItem("refresh");
  
      const refreshRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
  
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem("access", data.access);
  
        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            Authorization: `Bearer ${data.access}`,
            "Content-Type": "application/json",
          },
        });
      } else {
        logout()
        throw new Error("Token refresh failed");
      }
    }
  
    return res;
  };
  