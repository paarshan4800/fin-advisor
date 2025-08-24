import React, { createContext, useContext, useState } from "react";

const UserContext = createContext(undefined);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    _id: "ba12171d-653b-4193-be99-ce8d8b1fc3c1",
    created_at: "2025-08-23T16:44:15.679000",
    email: "kellypena@example.net",
    name: "Douglas Kelly",
    updated_at: "2025-08-23T16:44:15.679000",
  });

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

// Custom hook for easy access
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};
