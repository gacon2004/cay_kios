import React, { useState } from "react";
import axios from "axios";

function LoginPage() {
  const [cccd, setCccd] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError(""); // Xóa lỗi cũ
    
    // Kiểm tra CCCD không được rỗng
    if (!cccd) {
      setError("Vui lòng nhập CCCD.");
      return;
    }

    try {
      // BƯỚC 1: GỌI API ĐĂNG NHẬP
      const loginRes = await axios.post("http://localhost:8000/auth/patient/login", {
        national_id: cccd,
      });

      // Kiểm tra và lưu access_token
      if (loginRes.data && loginRes.data.token && loginRes.data.token.access_token) {
        localStorage.setItem("token", loginRes.data.token.access_token);
        
        // BƯỚC 2: GỌI API KIỂM TRA BẢO HIỂM
        try {
          const insuranceRes = await axios.get(`http://localhost:8000/insurances/check/${cccd}`);
          
          // Kiểm tra và lưu kết quả bảo hiểm
          if (insuranceRes.data && typeof insuranceRes.data.has_insurance !== 'undefined') {
            localStorage.setItem("has_insurance", insuranceRes.data.has_insurance);
            console.log("Thông tin bảo hiểm đã được lưu:", insuranceRes.data.has_insurance);
          }
        } catch (insuranceErr) {
          console.error("Lỗi khi kiểm tra bảo hiểm:", insuranceErr);
          // Bạn có thể chọn hiển thị lỗi này hoặc không, tùy thuộc vào UX
          // setError("Lỗi khi kiểm tra bảo hiểm.");
          localStorage.setItem("has_insurance", false); // Giả sử không có bảo hiểm nếu lỗi
        }

        alert("Đăng nhập thành công");
        window.location.href = "/appointment";
      } else {
        setError("Không nhận được token từ server.");
      }
    } catch (err) {
      console.error(err);
      setError("Đăng nhập thất bại. Vui lòng kiểm tra lại CCCD.");
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