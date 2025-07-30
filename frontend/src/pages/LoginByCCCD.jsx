import React, { useState } from "react";
import axios from "axios";

function LoginPage() {
  const [cccd, setCccd] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      const res = await axios.post("http://localhost:8000/auth/patient/token-by-cccd", {
        national_id: cccd,
      });

      // Kiểm tra response và lưu access_token
      if (res.data && res.data.token && res.data.token.access_token) {
        localStorage.setItem("token", res.data.token.access_token);
        setError("");
        alert("Đăng nhập thành công");
        window.location.href = "/appointment";
      } else {
        setError("Không nhận được token từ server.");
      }
    } catch (err) {
      console.error(err);
      setError("Đăng nhập thất bại.");
    }
  };

  return (
    <div>
      <h2>Đăng nhập bằng CCCD</h2>
      <input
        type="text"
        placeholder="Nhập CCCD"
        value={cccd}
        onChange={(e) => setCccd(e.target.value)}
      />
      <button onClick={handleLogin}>Đăng nhập</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default LoginPage;
