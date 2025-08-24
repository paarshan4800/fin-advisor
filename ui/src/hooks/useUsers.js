import React, { useEffect } from "react";
import { useState } from "react";
import api from "../api";

function useUsers() {
  const [usersData, setusersData] = useState([]);
  const [usersLoading, setusersLoading] = useState(false);
  const [usersError, setusersError] = useState(null);

  const GET_ALL_USERS_URI = "/users/all";

  const fetchUsers = async () => {
    setusersLoading(true);

    try {
      const resp = await api.get(GET_ALL_USERS_URI);
      console.log(resp);
      setusersData(resp.data.data.items);
    } catch (e) {
      setusersError(e.message);
    } finally {
      setusersLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return {
    usersData,
    usersLoading,
    usersError,
  };
}

export default useUsers;
