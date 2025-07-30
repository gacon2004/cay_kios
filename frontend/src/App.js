import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserList from './components/UserList';
import AppointmentPage from './pages/AppointmentPage';
import LoginByCCCD from "./pages/LoginByCCCD";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/users" element={<UserList />} />
                <Route path="/" element={<LoginByCCCD />} />
                <Route path="/appointment" element={<AppointmentPage />} />
            </Routes>
        </Router>
    );
}

export default App;
