// src/routes/RequireAuth.jsx
import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

function hasAccessToken() {
  return Boolean(localStorage.getItem("access_token"));
}

export default function RequireAuth() {
  const location = useLocation();

  if (!hasAccessToken()) {
    return <Navigate to="/signin" replace state={{ from: location }} />;
  }
  return <Outlet />;
}
