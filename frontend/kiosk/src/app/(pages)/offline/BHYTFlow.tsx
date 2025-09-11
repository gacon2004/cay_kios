'use client';

import PatientInfo from '@/app/components/PatientInfo';
import PrintTicket from '@/app/components/PrintTicket';
import ProgressBar from '@/app/components/ProgressBar';
import ServiceSelection from '@/app/components/ServiceSelection';
import { useAppContext } from '@/app/context/AppContext';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import React, { useEffect } from 'react';

const BHYTFlow = () => {
    const { currentStep, setCurrentStep } = useAppContext();
    const router = useRouter();

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

    const renderStep = () => {
        switch (currentStep) {
            case 1:
                return <PatientInfo />;
            case 2:
                return <ServiceSelection />;
            case 3:
                return <PrintTicket />;
            default:
                return <PatientInfo />;
        }
    };
    return (
        <div className="min-h-screen">
            {/* Header */}
            <div className="bg-background shadow-sm border-b border-[#e4e6eb]">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => handleBack()}
                            className="flex items-center space-x-2 text-while hover:text-gray-900 transition-colors duration-200 cursor-pointer"
                        >
                            <ArrowLeft size={24} />
                            <span className="text-lg text-while">Quay lại</span>
                        </button>

                        <h1 className="text-2xl font-bold text-while">
                            Đăng Ký Khám Bệnh BHYT
                        </h1>
                        <div className="w-24"></div>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <ProgressBar />

            {/* Main Content */}
            <div className="bg-[#e6ecff] min-h-[calc(100vh-154.5px)]">
                <div className="max-w-6xl mx-auto px-6 py-[37px] pb-20 ">
                    {renderStep()}
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full p-5 bg-background text-center text-text fixed bottom-0">
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

export default BHYTFlow;
