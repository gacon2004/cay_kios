import React, { useEffect, useState } from 'react';
import { getAllUsers } from '../api/user';

const UserList = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        getAllUsers().then(data => setUsers(data));
    }, []);

    return (
        <div style={{ padding: '20px' }}>
            <h2>📋 Danh sách người dùng</h2>
            {users.length === 0 ? (
                <p>Không có dữ liệu.</p>
            ) : (
                <table border="1" cellPadding="10" style={{ borderCollapse: 'collapse', width: '100%' }}>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>CCCD/CMND</th>
                            <th>Họ tên</th>
                            <th>Ngày sinh</th>
                            <th>Giới tính</th>
                            <th>Số điện thoại</th>
                            <th>Nghề nghiệp</th>
                            <th>Dân tộc</th>
                            <th>Ngày tạo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.national_id}</td>
                                <td>{user.full_name}</td>
                                <td>{user.date_of_birth}</td>
                                <td>{user.gender}</td>
                                <td>{user.phone}</td>
                                <td>{user.occupation}</td>
                                <td>{user.ethnicity}</td>
                                <td>{new Date(user.created_at).toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default UserList;
