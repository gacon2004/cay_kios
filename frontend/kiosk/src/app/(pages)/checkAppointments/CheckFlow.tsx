'use client';

import React, { useEffect, useState } from 'react';
import { ArrowLeft, Eye, EyeOff } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAppContext } from '@/app/context/AppContext';
import AppointmentCheck from './AppointmentCheck';
import PatientInfo from '@/app/components/PatientInfo';

const CheckFlow: React.FC = () => {
    const { currentStep, setCurrentStep } = useAppContext();
    const router = useRouter();
    const [showPatientInfo, setShowPatientInfo] = useState<boolean>(true); // State để ẩn/hiện PatientInfo

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    useEffect(() => {
        if (currentStep === 0) {
            router.push('/');
            setCurrentStep(1);
        }
    }, [currentStep]);

    return (
        <div className="min-h-screen">
            {/* Header */}
            <div className="bg-background shadow-sm border-b border-[#e4e6eb]">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => handleBack()}
                            className="flex items-center space-x-2 text-white hover:text-gray-900 transition-colors duration-200 cursor-pointer"
                        >
                            <ArrowLeft size={24} />
                            <span className="text-lg">Quay lại</span>
                        </button>
                        <h1 className="text-2xl font-bold text-white">
                            Kiểm Tra Lịch Hẹn
                        </h1>
                        <div className="w-24"></div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="bg-[#e6ecff] min-h-[calc(100vh-65px)] mb-10">
                <div className="max-w-7xl mx-auto px-6 py-8">
                    <div className="bg-white rounded-2xl shadow-lg p-3">
                        <div className="flex justify-end items-center">
                            <button
                                onClick={() =>
                                    setShowPatientInfo(!showPatientInfo)
                                }
                                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
                            >
                                {showPatientInfo ? (
                                    <>
                                        <EyeOff size={20} />
                                        <span>Ẩn thông tin bệnh nhân</span>
                                    </>
                                ) : (
                                    <>
                                        <Eye size={20} />
                                        <span>Hiện thông tin bệnh nhân</span>
                                    </>
                                )}
                            </button>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-1 gap-4">
                            {/* Patient Information */}
                            <div>
                                {showPatientInfo ? (
                                    <PatientInfo />
                                ) : (
                                    <p className="text-gray-600 text-center">
                                        Thông tin bệnh nhân đã được ẩn.
                                    </p>
                                )}
                            </div>

                            {/* Appointment List */}
                            <AppointmentCheck />
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full p-4 bg-background text-center text-text fixed bottom-0">
                <div className="max-w-6xl mx-auto ">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="text-sm text-while">
                                Phiên bản: v1.0.0
                            </div>
                        </div>
                        <div className="text-sm text-while">
                            © 2025 Hệ Thống Y Tế
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default CheckFlow;
