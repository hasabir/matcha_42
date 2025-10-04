import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

export default function ConfirmReset() {
  const navigate = useNavigate();
  const { token: tokenFromPath } = useParams();
  const [sp] = useSearchParams();
  const token = tokenFromPath || sp.get("token") || "";
  const [err, setErr] = useState(null);

  useEffect(() => {
    const run = async () => {
      if (!token) {
        setErr("Missing token");
        return;
      }
      try {
        const res = await fetch(
          `http://localhost:5000/api/auth/confirm_email_reset/${encodeURIComponent(
            token
          )}`
        );
        const data = await res.json().catch(() => ({}));
        if (!res.ok || data.status !== "ok") {
          throw new Error(data?.error || "Confirmation failed");
        }
        // pass only token; username will be typed on next page if needed
        navigate(`/reset-password?token=${encodeURIComponent(data.token)}`);
      } catch (e) {
        setErr(e.message);
      }
    };
    run();
  }, [token, navigate]);

  if (err) return <div className="rp-msg err">{err}</div>;
  return <div>Validating your reset link…</div>;
}
