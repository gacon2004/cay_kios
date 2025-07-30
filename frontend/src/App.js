import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppointmentPage from './pages/AppointmentPage';
import LoginByCCCD from "./pages/LoginByCCCD";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LoginByCCCD />} />
                <Route path="/appointment" element={<AppointmentPage />} />
            </Routes>
        </Router>
    );
}

export default App;
