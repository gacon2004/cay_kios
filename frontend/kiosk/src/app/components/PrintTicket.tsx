'use client';

import React, { useState } from 'react';
import { Printer, User, Stethoscope, QrCode } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import Image from 'next/image';

const PrintTicket: React.FC = () => {
    const { patient, selectedService, appointment, resetApp } = useAppContext();
    const [showPrintModal, setShowPrintModal] = useState(false);

    const handlePrint = () => {
        setShowPrintModal(true);
        // In a real implementation, this would send the print command to the thermal printer
        setTimeout(() => {
            setShowPrintModal(false);
            alert('Phiếu khám đã được in thành công!');
            // Auto-return to main screen after printing
            setTimeout(() => {
                resetApp();
            }, 2000);
        }, 3000);
    };

    if (!patient || !selectedService || !appointment) {
        return (
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-2xl shadow-lg p-8">
                    <div className="text-center text-red-600">
                        <p>Thông tin không đầy đủ. Vui lòng thử lại.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Hoàn Thành Đăng Ký
                    </h2>
                    <p className="text-gray-600">
                        Kiểm tra thông tin và in phiếu khám
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Patient Information */}
                    <div className="bg-blue-50 rounded-xl p-6">
                        <div className="flex items-center mb-4">
                            <User className="text-blue-500 mr-2" size={24} />
                            <h3 className="text-xl font-semibold text-gray-900">
                                Thông Tin Bệnh Nhân
                            </h3>
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Họ tên:</span>
                                <span className="font-semibold">
                                    {patient.full_name}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">CCCD:</span>
                                <span className="font-semibold font-mono">
                                    {patient.national_id}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Ngày sinh:
                                </span>
                                <span className="font-semibold">
                                    {patient.date_of_birth}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Giới tính:
                                </span>
                                <span className="font-semibold">
                                    {patient.gender}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">SĐT:</span>
                                <span className="font-semibold">
                                    {patient.phone}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Appointment Information */}
                    <div className="bg-green-50 rounded-xl p-6">
                        <div className="flex items-center mb-4">
                            <Stethoscope
                                className="text-green-500 mr-2"
                                size={24}
                            />
                            <h3 className="text-xl font-semibold text-gray-900">
                                Thông Tin Khám
                            </h3>
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Dịch vụ:</span>
                                <span className="font-semibold">
                                    {selectedService.name}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Phòng:</span>
                                <span className="font-semibold">
                                    {appointment.clinic_name}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Bác sĩ:</span>
                                <span className="font-semibold">
                                    {appointment.doctor_name}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Số thứ tự:
                                </span>
                                <span className="font-semibold text-2xl text-green-600">
                                    {appointment.queue_number}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Thời gian:
                                </span>
                                <span className="font-semibold">
                                    {new Date(
                                        appointment.appointment_time
                                    ).toLocaleString('vi-VN', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric',
                                    })}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* QR Code */}
                {appointment.qr_code ? (
                    <div className="mt-8 text-center">
                        <div className="bg-gray-50 rounded-xl p-6 inline-block">
                            <div className="flex items-center justify-center mb-4">
                                <QrCode
                                    className="text-gray-500 mr-2"
                                    size={20}
                                />
                                <span className="text-gray-700">
                                    Mã QR để check-in
                                </span>
                            </div>
                            <div className="w-32 h-32 bg-white rounded-lg flex items-center justify-center mx-auto">
                                <Image
                                    src={`data:image/png;base64,${appointment.qr_code}`}
                                    alt="QR Code"
                                    width={128}
                                    height={128}
                                    unoptimized
                                />
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="mt-8 text-center">
                        <div className="bg-gray-100 rounded-xl p-6 inline-block">
                            <div className="flex items-center justify-center mb-4">
                                <QrCode
                                    className="text-gray-400 mr-2"
                                    size={20}
                                />
                                <span className="text-gray-500">
                                    Vui lòng đăng nhập để xem mã QR
                                </span>
                            </div>
                            <div className="w-32 h-32 bg-white rounded-lg flex items-center justify-center mx-auto">
                                <Image
                                    src="/images/placeholder-qr.png"
                                    alt="QR Placeholder"
                                    width={128}
                                    height={128}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Print Button */}
                <div className="mt-8 text-center">
                    <button
                        onClick={handlePrint}
                        className="bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-12 rounded-xl transition-colors duration-200 text-lg flex items-center mx-auto"
                    >
                        <Printer className="mr-3" size={24} />
                        In Phiếu Khám
                    </button>
                </div>

                {/* Instructions */}
                <div className="mt-8 bg-yellow-50 rounded-xl p-6">
                    <h4 className="font-semibold text-gray-900 mb-3">
                        Hướng dẫn:
                    </h4>
                    <ul className="space-y-2 text-gray-700">
                        <li>• Vui lòng đến phòng khám đúng giờ hẹn</li>
                        <li>• Mang theo phiếu khám và giấy tờ tùy thân</li>
                        <li>• Liên hệ tổng đài nếu cần hỗ trợ</li>
                    </ul>
                </div>
            </div>

            {/* Print Modal */}
            {showPrintModal && (
                <div className="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50">
                    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm mx-4">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500 mx-auto mb-4"></div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Đang in phiếu khám...
                            </h3>
                            <p className="text-gray-600">
                                Vui lòng chờ trong giây lát
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PrintTicket;
