'use client';

import React, { useState, useEffect } from 'react';
import { Stethoscope, DollarSign, MapPin, Clock } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import RoomModal from './RoomModal';
import type { Service, Room } from '../context/AppContext';
import api from '../axios/api';

const ServiceSelection: React.FC = () => {
    const {
        setCurrentStep,
        selectedService,
        setSelectedService,
        setAppointment,
    } = useAppContext();
    const [services, setServices] = useState<Service[]>([]);
    const [showRoomModal, setShowRoomModal] = useState(false);
    const [loading, setLoading] = useState(true);

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

    const handleRoomSelect = async (room: Room) => {
        if (!selectedService) return;
        const appointmentData = await api.post(`/appointments/?has_insurances=${localStorage.getItem("has_insurances")}`, {
            service_id: selectedService.id,
            clinic_id: room.clinic_id,
            doctor_id: room.doctor_id,
        });

        setAppointment(appointmentData?.data);
        setShowRoomModal(false);
        setCurrentStep(3);
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
                                <div className="bg-blue-500 rounded-lg p-3">
                                    <Stethoscope
                                        className="text-white"
                                        size={24}
                                    />
                                </div>
                                <div className="text-right">
                                    <div className="flex items-center text-green-600 font-semibold">
                                        <DollarSign
                                            size={16}
                                            className="mr-1"
                                        />
                                        {service.price.toLocaleString()} VND
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
                                <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200">
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
        </div>
    );
};

export default ServiceSelection;
