'use client';

import React, { useState, useEffect } from 'react';
import { Printer, User, Stethoscope, QrCode, CheckCircle } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import Image from 'next/image';
import api from '../axios/api';

const PrintTicket: React.FC = () => {
    const { patient, selectedService, appointment, resetApp } = useAppContext();
    const [showPrintModal, setShowPrintModal] = useState(false);
    const [QR, setQR] = useState<string | undefined>();
    const [Timepayment, setTimepayment] = useState<Date | null>(null);
    const [paymentStatus, setPaymentStatus] = useState('PENDING');
    const [orderCode, setOrderCode] = useState<string | null>(null);
    const [timeLeft, setTimeLeft] = useState<number>(15 * 60); // 15 minutes in seconds

    // Handle printing
    const handlePrint = async () => {
        if (!appointment?.id) {
            alert('Không tìm thấy thông tin cuộc hẹn!');
            return;
        }

        setShowPrintModal(true);
        try {
            const response = await api.get(
                `/appointments/${appointment.id}/print-ticket`,
                {
                    responseType: 'blob',
                }
            );

            if (response.status !== 200) {
                throw new Error('Lỗi khi tải phiếu khám');
            }

            const blob = response.data;
            const url = window.URL.createObjectURL(blob);

            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
            iframe.src = url;

            iframe.onload = () => {
                try {
                    iframe.contentWindow?.print();
                } catch (error) {
                    console.error('Lỗi khi in:', error);
                    alert('Có lỗi xảy ra khi in phiếu khám');
                } finally {
                    document.body.removeChild(iframe);
                    window.URL.revokeObjectURL(url);
                }
            };

            const pdfUrl = window.URL.createObjectURL(blob);
            window.open(pdfUrl, '_blank');
            setTimeout(() => {
                window.URL.revokeObjectURL(pdfUrl);
            }, 1000);

            setTimeout(() => {
                setShowPrintModal(false);
                alert('Phiếu khám đã được in và mở trong tab mới!');
                setTimeout(() => {
                    resetApp();
                }, 2000);
            }, 3000);
        } catch (error) {
            console.error('Lỗi:', error);
            setShowPrintModal(false);
            alert('Có lỗi xảy ra khi tải phiếu khám');
        }
    };

    // Fetch QR code
    const fetchQR = async () => {
        if (appointment?.id) {
            try {
                const qrResponse = await api.post('/payments/orders', {
                    appointment_id: appointment.id,
                });
                setQR(qrResponse.data.qr_code_url);
                setTimepayment(qrResponse.data.paid_at || null);
                setOrderCode(qrResponse.data.order_code);
                setTimeLeft(15 * 60); // Reset timer to 15 minutes when QR is fetched
            } catch (error) {
                console.error('Lỗi khi lấy QR:', error);
            }
        }
    };

    // Check payment status
    const checkPaymentStatus = async () => {
        if (orderCode) {
            try {
                const response = await api.get(`/payments/orders/${orderCode}`);
                setPaymentStatus(response.data.status);
            } catch (error) {
                console.error('Lỗi khi kiểm tra trạng thái thanh toán:', error);
            }
        }
    };

    // Countdown timer effect
    useEffect(() => {
        let timer: NodeJS.Timeout | null = null;
        if (QR && paymentStatus !== 'PAID' && timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        clearInterval(timer!);
                        // Handle QR expiration (e.g., fetch new QR or show message)
                        alert('Mã QR đã hết hạn. Vui lòng tạo mã mới.');
                        fetchQR(); // Optionally fetch a new QR code
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => {
            if (timer) clearInterval(timer);
        };
    }, [QR, paymentStatus, timeLeft]);

    // Fetch QR on mount
    useEffect(() => {
        fetchQR();
    }, []);

    // Poll payment status
    useEffect(() => {
        let interval: NodeJS.Timeout | null = null;
        if (orderCode && paymentStatus !== 'PAID') {
            interval = setInterval(checkPaymentStatus, 5000);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [orderCode, paymentStatus]);

    // Format timeLeft to mm:ss
    const formatTime = (seconds: number): string => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs
            .toString()
            .padStart(2, '0')}`;
    };

    if (!patient || !selectedService || !appointment) {
        return (
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-2xl shadowNg p-8">
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
                    <h2 className="text-4xl font-bold text-gray-900 mb-2">
                        Hoàn Thành Đăng Ký
                    </h2>
                    <p className="text-gray-600 text-lg">
                        Kiểm tra thông tin và in phiếu khám
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-1 gap-8 text-xl">
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
                                <span className="text-gray-600">Giá:</span>
                                <span className="font-semibold text-2xl text-green-600">
                                    {appointment.cur_price.toLocaleString(
                                        'vi-VN',
                                        {
                                            style: 'currency',
                                            currency: 'VND',
                                        }
                                    )}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Thời gian dự kiến đến lượt:
                                </span>
                                <span className="font-semibold">
                                    {new Date(
                                        appointment.estimated_time
                                    ).toLocaleString('vi-VN', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric',
                                    })}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Trạng thái thanh toán:
                                </span>
                                <span
                                    className={`font-semibold ${
                                        paymentStatus === 'PAID'
                                            ? 'text-green-600'
                                            : 'text-red-500'
                                    }`}
                                >
                                    {paymentStatus === 'PAID'
                                        ? 'Đã thanh toán'
                                        : 'Đang chờ thanh toán'}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Thời gian thanh toán:
                                </span>
                                <span className="font-semibold">
                                    {Timepayment?.toLocaleString('vi-VN', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric',
                                    }) ?? 'Chưa có thời gian'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Payment Status or QR Code */}
                {paymentStatus === 'PAID' ? (
                    <div className="mt-8 text-center">
                        <div className="bg-green-50 rounded-xl p-6 inline-block">
                            <div className="flex items-center justify-center mb-4">
                                <span className="text-green-700 font-semibold text-2xl">
                                    Thanh toán thành công
                                </span>
                            </div>
                            <div className="w-32 h-32 bg-white rounded-lg flex items-center justify-center mx-auto">
                                <CheckCircle
                                    className="text-green-500"
                                    size={64}
                                />
                            </div>
                        </div>
                    </div>
                ) : QR ? (
                    <div className="mt-8 text-center">
                        <div className="bg-gray-50 rounded-xl p-6 inline-block">
                            <div className="flex items-center justify-center mb-4">
                                <QrCode
                                    className="text-gray-500 mr-2"
                                    size={20}
                                />
                                <span className="text-gray-700">
                                    Mã QR để thanh toán
                                </span>
                            </div>
                            <div className="w-40 h-40 bg-white rounded-lg flex items-center justify-center mx-auto">
                                <Image
                                    src={QR}
                                    alt="QR Code"
                                    width={160}
                                    height={160}
                                    unoptimized
                                />
                            </div>
                            <div className="mt-4">
                                <span className="text-red-600 font-semibold text-lg">
                                    Thời gian còn lại: {formatTime(timeLeft)}
                                </span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="mt-8 text-center">
                        <div className="bg-gray-100 rounded-xl p-6 inline-block">
                            <div className="flex items-center justify-center mb-4">
                                <QrCode
                                    className="text-gray-400 mr-2"
                                    size={25}
                                />
                                <span className="text-gray-500">
                                    Vui lòng đăng nhập để xem mã QR
                                </span>
                            </div>
                            <div className="w-32 h-32 bg-white rounded-lg flex items-center justify-center mx-auto">
                                <Image
                                    src="/images/placeholder-qr.png"
                                    alt="QR Placeholder"
                                    width={200}
                                    height={200}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Print Button */}
                <div className="mt-8 text-center">
                    <button
                        onClick={handlePrint}
                        disabled={paymentStatus !== 'PAID'}
                        className={`font-semibold py-4 px-12 rounded-xl transition-colors duration-200 text-lg flex items-center mx-auto ${
                            paymentStatus === 'PAID'
                                ? 'bg-green-500 hover:bg-green-600 text-white'
                                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                        }`}
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
                        <li>
                            • Vui lòng hoàn tất thanh toán trước khi in phiếu
                            khám
                        </li>
                        <li>
                            • Mã QR sẽ hết hạn sau 15 phút. Vui lòng thanh toán
                            trong thời gian này.
                        </li>
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
