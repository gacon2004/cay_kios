/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState, useEffect } from 'react';
import { Stethoscope, MapPin, Clock } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { usePathname } from 'next/navigation';
import RoomModal from './RoomModal';
import PickCalendar from './PickCalender';
import type { Service, Room } from '../context/AppContext';
import api from '../axios/api';
import { useToast } from '@/app/components/ui/use-toast';

const ServiceSelection: React.FC = () => {
    const {
        setCurrentStep,
        selectedService,
        setSelectedService,
        setAppointment,
    } = useAppContext();
    const [services, setServices] = useState<Service[]>([]);
    const [showRoomModal, setShowRoomModal] = useState(false);
    const [showCalendarModal, setShowCalendarModal] = useState(false);
    const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
    const [loading, setLoading] = useState(true);
    const pathname = usePathname();
    const { toast } = useToast();

    useEffect(() => {
        const fetchServices = async () => {
            setLoading(true);
            const data = await api.get(`/services/`);
            setServices(data?.data);
            setLoading(false);
        };

        fetchServices();
    }, []);

    const handleServiceSelect = (service: Service) => {
        setSelectedService(service);
        setShowRoomModal(true);
    };

    const handleRoomSelect = (room: Room) => {
        setSelectedRoom(room);
        setShowRoomModal(false);
        if (pathname === '/online') {
            setShowCalendarModal(true);
        } else if (pathname === '/offline') {
            handleScheduleSelect('', 0, room);
        }
    };

    const handleScheduleSelect = async (
        work_date: string,
        schedule_id: number,
        roomOverride?: Room
    ) => {
        const roomToUse = roomOverride || selectedRoom;
        if (!selectedService || !roomToUse) return;

        try {
            const isOnline = pathname === '/online';
            const apiEndpoint = isOnline
                ? `/appointments/book-online?has_insurances=${localStorage.getItem(
                      'has_insurances'
                  )}`
                : `/appointments/book-offline?has_insurances=${localStorage.getItem(
                      'has_insurances'
                  )}`;

            const appointmentData = await api.post(apiEndpoint, {
                service_id: selectedService.id,
                clinic_id: roomToUse.clinic_id,
                doctor_id: roomToUse.doctor_id,
                ...(isOnline && { schedule_id }),
            });

            setAppointment(appointmentData?.data);
            setShowCalendarModal(false);
            setCurrentStep(3);
        } catch (error: any) {
            console.error('Failed to create appointment:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
            });
            const errorMessage =
                error.response?.data?.detail || 'Đã có lỗi xảy ra khi đặt lịch';
            toast({
                title: 'Lỗi đặt lịch',
                description: errorMessage,
            });
        }
    };

    if (loading) {
        return (
            <div className="max-w-6xl mx-auto">
                <div className="bg-white rounded-2xl shadow-lg p-8">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                        <p className="text-gray-600 mt-4">
                            Đang tải danh sách dịch vụ...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Chọn Dịch Vụ Khám
                    </h2>
                    <p className="text-gray-600">
                        Chọn dịch vụ y tế phù hợp với nhu cầu của bạn
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {services.map(service => (
                        <div
                            key={service.id}
                            className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
                            onClick={() => handleServiceSelect(service)}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="bg-background rounded-lg p-3">
                                    <Stethoscope
                                        className="text-white"
                                        size={24}
                                    />
                                </div>
                                <div className="text-right">
                                    <div className="flex items-center text-green-600 font-semibold">
                                        {service.price.toLocaleString('vi-VN', {
                                            style: 'currency',
                                            currency: 'VND',
                                            currencyDisplay: 'code',
                                        })}
                                    </div>
                                </div>
                            </div>

                            <h3 className="text-lg font-semibold text-gray-900 mb-2 capitalize">
                                {service.name}
                            </h3>

                            <div className="flex items-center text-gray-600 mb-3">
                                <MapPin size={16} className="mr-2" />
                                <span className="text-sm">
                                    {service.description}
                                </span>
                            </div>

                            <div className="flex items-center text-gray-500">
                                <Clock size={16} className="mr-2" />
                                <span className="text-sm">
                                    Thời gian: ~30 phút
                                </span>
                            </div>

                            <div className="mt-4 pt-4 border-t border-blue-200">
                                <button className="w-full bg-background hover:opacity-80 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200">
                                    Chọn dịch vụ này
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {services.length === 0 && (
                    <div className="text-center py-8">
                        <div className="text-gray-400 mb-4">
                            <Stethoscope size={48} className="mx-auto" />
                        </div>
                        <p className="text-gray-600">
                            Không có dịch vụ khám nào khả dụng
                        </p>
                    </div>
                )}
            </div>

            {showRoomModal && selectedService && (
                <RoomModal
                    service={selectedService}
                    onRoomSelect={handleRoomSelect}
                    onClose={() => setShowRoomModal(false)}
                />
            )}

            {showCalendarModal && selectedRoom && selectedService && (
                <PickCalendar
                    room={selectedRoom}
                    service={selectedService}
                    onScheduleSelect={handleScheduleSelect}
                    onClose={() => setShowCalendarModal(false)}
                />
            )}
        </div>
    );
};

export default ServiceSelection;
