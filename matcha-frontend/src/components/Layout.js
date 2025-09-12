// In src/components/Layout.js
import React from "react";

export default function Layout({ children }) {
  return (
    <>
      <header className="site-header">
        <h1 className="brand">matcha</h1>
        {/* Put your sign‑in/up button here */}
      </header>
      <main>{children}</main>
    </>
  );
}
