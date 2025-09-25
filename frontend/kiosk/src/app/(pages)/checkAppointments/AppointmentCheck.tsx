/* eslint-disable react-hooks/exhaustive-deps */
'use client';

import React, { useState, useEffect } from 'react';
import { Stethoscope, Trash2, CheckCircle, CreditCard } from 'lucide-react';
import {
    useAppContext,
    Appointment,
    PaymentInfo,
} from '@/app/context/AppContext';
import api from '@/app/axios/api';
import PrintTicket from '@/app/components/PrintTicket';

const AppointmentCheck: React.FC = () => {
    const { patient, setAppointment, setSelectedService, setOrderCode } =
        useAppContext();
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [successMessage, setSuccessMessage] = useState<string>('');
    const [page, setPage] = useState<number>(1);
    const [limit] = useState<number>(10);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const [fromDate, setFromDate] = useState<string>('');
    const [toDate, setToDate] = useState<string>('');
    const [statusFilter, setStatusFilter] = useState<number | null>(null);
    const [payStatus, setPayStatus] = useState<string | null>(null);
    const [showPrintTicket, setShowPrintTicket] = useState<boolean>(false);
    const [selectedAppointment, setSelectedAppointment] =
        useState<Appointment | null>(null);

    // Lấy danh sách lịch hẹn và kiểm tra lịch hẹn quá hạn
    useEffect(() => {
        if (patient?.national_id) {
            fetchAppointments(patient.national_id);
        } else {
            setAppointments([]);
            setHasMore(false);
        }
    }, [patient, page, fromDate, toDate, statusFilter, payStatus]);

    const fetchAppointments = async (nationalId: string) => {
        setLoading(true);
        setError('');
        try {
            const offset = (page - 1) * limit;
            const currentDate = new Date('2025-09-12T00:00:00+07:00');

            if (payStatus) {
                const paymentParams = new URLSearchParams({
                    limit: limit.toString(),
                    offset: offset.toString(),
                    ...(fromDate && { from_date: fromDate }),
                    ...(toDate && { to_date: toDate }),
                    pay_status: payStatus,
                });

                const paymentResponse = await api.get<PaymentInfo[]>(
                    `/appointments/patient/payment/me?${paymentParams.toString()}`
                );
                const paymentData = paymentResponse.data;

                const convertedAppointments = paymentData.map(payment => ({
                    id: 0,
                    patient_id: 0,
                    clinic_id: 0,
                    service_id: 0,
                    doctor_id: 0,
                    schedule_id: 0,
                    queue_number: payment.queue_number,
                    shift_number: payment.shift_number,
                    estimated_time: payment.estimated_time,
                    printed: 0,
                    status: 1,
                    booking_channel: '',
                    cur_price: payment.price_vnd,
                    service_name: payment.service_name,
                    service_price: payment.price_vnd,
                    doctor_name: payment.doctor_name,
                    clinic_name: payment.clinic_name,
                    payment_info: payment,
                }));

                for (const appointment of convertedAppointments) {
                    const estimatedTime = new Date(appointment.estimated_time);
                    if (
                        estimatedTime < currentDate &&
                        appointment.status !== 4
                    ) {
                        await api.post(
                            `/appointments/${appointment.id}/cancel`
                        );
                        appointment.status = 4;
                    }
                }

                setAppointments(convertedAppointments);
                setHasMore(paymentData.length === limit);
            } else {
                const appointmentParams = new URLSearchParams({
                    limit: limit.toString(),
                    offset: offset.toString(),
                    ...(fromDate && { from_date: fromDate }),
                    ...(toDate && { to_date: toDate }),
                    ...(statusFilter !== null && {
                        status_filter: statusFilter.toString(),
                    }),
                });

                const appointmentResponse = await api.get<Appointment[]>(
                    `/appointments/partient/me?${appointmentParams.toString()}`
                );
                const appointmentsData = appointmentResponse.data;

                const paymentParams = new URLSearchParams({
                    limit: limit.toString(),
                    offset: offset.toString(),
                    ...(fromDate && { from_date: fromDate }),
                    ...(toDate && { to_date: toDate }),
                });

                const paymentResponse = await api.get<PaymentInfo[]>(
                    `/appointments/patient/payment/me?${paymentParams.toString()}`
                );
                const paymentData = paymentResponse.data;

                const paymentMap = new Map<string, PaymentInfo>();
                paymentData.forEach(payment => {
                    if (payment.estimated_time) {
                        paymentMap.set(payment.estimated_time, payment);
                    }
                });

                const appointmentsWithPayment = appointmentsData.map(
                    appointment => ({
                        ...appointment,
                        payment_info: paymentMap.get(
                            appointment.estimated_time
                        ),
                    })
                );

                for (const appointment of appointmentsWithPayment) {
                    const estimatedTime = new Date(appointment.estimated_time);
                    if (
                        estimatedTime < currentDate &&
                        appointment.status !== 4
                    ) {
                        await api.post(
                            `/appointments/${appointment.id}/cancel`
                        );
                        appointment.status = 4;
                    }
                }

                setAppointments(appointmentsWithPayment);
                setHasMore(appointmentsData.length === limit);
            }
        } catch (err) {
            setError('Không thể tải danh sách lịch hẹn. Vui lòng thử lại.');
            console.error('Lỗi khi lấy lịch hẹn:', err);
        } finally {
            setLoading(false);
        }
    };

    // Xử lý khi nhấn "Tiếp tục thanh toán"
    const handleContinuePayment = async (appointment: Appointment) => {
        setSelectedAppointment(appointment);
        setAppointment(appointment);
        setSelectedService({
            id: appointment.id.toString(),
            name: appointment.service_name,
            price: appointment.service_price || appointment.cur_price || 0,
            description: '',
        });
        if (appointment.payment_info?.order_code) {
            setOrderCode(appointment.payment_info.order_code);
        }
        setShowPrintTicket(true); // Chuyển sang PrintTicket
    };

    // Hủy lịch hẹn
    const handleCancelAppointment = async (appointmentId: number) => {
        if (confirm('Bạn có chắc chắn muốn hủy lịch hẹn này?')) {
            try {
                await api.post(`/appointments/${appointmentId}/cancel`);
                setSuccessMessage('Hủy lịch hẹn thành công!');
                if (patient?.national_id) {
                    await fetchAppointments(patient.national_id);
                }
                setTimeout(() => setSuccessMessage(''), 3000);
            } catch (err) {
                setError('Không thể hủy lịch hẹn. Vui lòng thử lại.');
                console.error('Lỗi khi hủy lịch hẹn:', err);
            }
        }
    };

    // Định dạng giá tiền
    const formatPrice = (price?: number): string => {
        if (price == null) {
            return 'N/A';
        }
        return price.toLocaleString('vi-VN', {
            style: 'currency',
            currency: 'VND',
        });
    };

    return (
        <div className="w-full mx-auto">
            {showPrintTicket && selectedAppointment ? (
                <PrintTicket />
            ) : (
                <div className="bg-green-50 rounded-xl p-6">
                    <div className="flex items-center mb-4">
                        <Stethoscope
                            className="text-green-500 mr-2"
                            size={24}
                        />
                        <h3 className="text-xl font-semibold text-gray-900">
                            Danh Sách Lịch Hẹn
                        </h3>
                    </div>

                    <div className="mb-6 grid grid-cols-1 md:grid-cols-5 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Từ ngày
                            </label>
                            <input
                                type="date"
                                value={fromDate}
                                onChange={e => setFromDate(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Đến ngày
                            </label>
                            <input
                                type="date"
                                value={toDate}
                                onChange={e => setToDate(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Trạng thái lịch hẹn
                            </label>
                            <select
                                value={statusFilter ?? ''}
                                onChange={e =>
                                    setStatusFilter(
                                        e.target.value
                                            ? parseInt(e.target.value)
                                            : null
                                    )
                                }
                                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Tất cả</option>
                                <option value="1">Đã xác nhận</option>
                                <option value="4">Đã hủy</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Trạng thái thanh toán
                            </label>
                            <select
                                value={payStatus ?? ''}
                                onChange={e =>
                                    setPayStatus(e.target.value || null)
                                }
                                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Tất cả</option>
                                <option value="PAID">Đã thanh toán</option>
                                <option value="AWAITING">Đang chờ</option>
                            </select>
                        </div>
                        <div className="flex items-end">
                            <button
                                onClick={() => {
                                    setPage(1);
                                    if (patient?.national_id) {
                                        fetchAppointments(patient.national_id);
                                    }
                                }}
                                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg transition-colors duration-200"
                            >
                                Tìm kiếm
                            </button>
                        </div>
                    </div>

                    <div className="relative h-full overflow-y-auto">
                        {loading ? (
                            <div className="text-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                                <p className="text-gray-600 mt-2">
                                    Đang tải lịch hẹn...
                                </p>
                            </div>
                        ) : appointments.length === 0 ? (
                            <p className="text-gray-600 text-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                                Không có lịch hẹn nào.
                            </p>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {appointments.map(appointment => (
                                    <div
                                        key={appointment.id}
                                        className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
                                    >
                                        <div className="space-y-2 text-lg">
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Dịch vụ:
                                                </span>
                                                <span className="font-semibold">
                                                    {appointment.payment_info
                                                        ?.service_name ||
                                                        appointment.service_name ||
                                                        'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Phòng:
                                                </span>
                                                <span className="font-semibold">
                                                    {appointment.payment_info
                                                        ?.clinic_name ||
                                                        appointment.clinic_name ||
                                                        'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Bác sĩ:
                                                </span>
                                                <span className="font-semibold">
                                                    {appointment.payment_info
                                                        ?.doctor_name ||
                                                        appointment.doctor_name ||
                                                        'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Số thứ tự:
                                                </span>
                                                <span className="font-semibold text-green-600">
                                                    {appointment.payment_info
                                                        ?.queue_number ||
                                                        appointment.queue_number ||
                                                        'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Giá:
                                                </span>
                                                <span className="font-semibold text-green-600">
                                                    {formatPrice(
                                                        appointment.payment_info
                                                            ?.price_vnd ||
                                                            appointment.cur_price
                                                    )}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Thời gian:
                                                </span>
                                                <span className="font-semibold">
                                                    {appointment.payment_info
                                                        ?.estimated_time ||
                                                    appointment.estimated_time
                                                        ? new Date(
                                                              appointment
                                                                  .payment_info
                                                                  ?.estimated_time ||
                                                                  appointment.estimated_time
                                                          ).toLocaleString(
                                                              'vi-VN',
                                                              {
                                                                  hour: '2-digit',
                                                                  minute: '2-digit',
                                                                  day: '2-digit',
                                                                  month: '2-digit',
                                                                  year: 'numeric',
                                                              }
                                                          )
                                                        : 'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Trạng thái:
                                                </span>
                                                <span
                                                    className={`font-semibold ${
                                                        appointment.status === 1
                                                            ? 'text-green-600'
                                                            : 'text-red-500'
                                                    }`}
                                                >
                                                    {appointment.status === 1
                                                        ? 'Đã xác nhận'
                                                        : 'Đã hủy'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">
                                                    Trạng thái thanh toán:
                                                </span>
                                                <span
                                                    className={`font-semibold ${
                                                        appointment.payment_info
                                                            ?.pay_status ===
                                                        'PAID'
                                                            ? 'text-green-600'
                                                            : appointment
                                                                  .payment_info
                                                                  ?.pay_status ===
                                                              'AWAITING'
                                                            ? 'text-yellow-500'
                                                            : 'text-red-500'
                                                    }`}
                                                >
                                                    {appointment.payment_info
                                                        ?.pay_status === 'PAID'
                                                        ? 'Đã thanh toán'
                                                        : appointment
                                                              .payment_info
                                                              ?.pay_status ===
                                                          'AWAITING'
                                                        ? 'Chờ thanh toán'
                                                        : 'Đã hết hạn'}
                                                </span>
                                            </div>
                                            {appointment.payment_info
                                                ?.pay_status === 'PAID' && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-600">
                                                        Thanh toán lúc:
                                                    </span>
                                                    <span className="font-semibold">
                                                        {appointment
                                                            .payment_info
                                                            ?.paid_at
                                                            ? new Date(
                                                                  appointment.payment_info.paid_at
                                                              ).toLocaleString(
                                                                  'vi-VN',
                                                                  {
                                                                      hour: '2-digit',
                                                                      minute: '2-digit',
                                                                      day: '2-digit',
                                                                      month: '2-digit',
                                                                      year: 'numeric',
                                                                  }
                                                              )
                                                            : 'N/A'}
                                                    </span>
                                                </div>
                                            )}
                                            {appointment.status === 1 &&
                                                appointment.payment_info
                                                    ?.pay_status !== 'PAID' && (
                                                    <div className="mt-2 space-y-2">
                                                        {appointment
                                                            .payment_info
                                                            ?.pay_status ===
                                                            'AWAITING' && (
                                                            <button
                                                                onClick={() =>
                                                                    handleContinuePayment(
                                                                        appointment
                                                                    )
                                                                }
                                                                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg transition-colors duration-200 flex items-center justify-center"
                                                            >
                                                                <CreditCard
                                                                    className="mr-2"
                                                                    size={20}
                                                                />
                                                                Tiếp tục thanh
                                                                toán
                                                            </button>
                                                        )}
                                                        <button
                                                            onClick={() =>
                                                                handleCancelAppointment(
                                                                    appointment.id
                                                                )
                                                            }
                                                            className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-2 rounded-lg transition-colors duration-200 flex items-center justify-center"
                                                        >
                                                            <Trash2
                                                                className="mr-2"
                                                                size={20}
                                                            />
                                                            Hủy lịch hẹn
                                                        </button>
                                                    </div>
                                                )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {appointments.length > 0 && (
                        <div className="mt-6 flex justify-center gap-4">
                            <button
                                onClick={() =>
                                    setPage(prev => Math.max(prev - 1, 1))
                                }
                                disabled={page === 1}
                                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
                            >
                                Trước
                            </button>
                            <span className="self-center">Trang {page}</span>
                            <button
                                onClick={() => setPage(prev => prev + 1)}
                                disabled={!hasMore}
                                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
                            >
                                Sau
                            </button>
                        </div>
                    )}

                    {successMessage && (
                        <div className="mt-8 bg-green-50 rounded-xl p-6 text-center">
                            <div className="flex items-center justify-center mb-4">
                                <CheckCircle
                                    className="text-green-500 mr-2"
                                    size={24}
                                />
                                <span className="text-green-700 font-semibold">
                                    {successMessage}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AppointmentCheck;
