'use client';

import { CheckCircle, User, Stethoscope, Printer } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const ProgressBar = () => {
    const { currentStep } = useAppContext();

    const steps = [
        {
            number: 1,
            title: 'Thông Tin Bệnh Nhân',
            icon: User,
        },
        {
            number: 2,
            title: 'Chọn Dịch Vụ',
            icon: Stethoscope,
        },
        {
            number: 3,
            title: 'In Phiếu Khám',
            icon: Printer,
        },
    ];

    return (
        <div className="bg-white w-full fixed z-50 border-b border-[#e4e6eb]">
            <div className="max-w-6xl mx-auto px-6 py-3 pt-18">
                <div className="flex items-center justify-between">
                    {steps.map((step, index) => (
                        <div key={step.number} className="flex items-center">
                            <div className="flex flex-row gap-2.5 items-center">
                                <div
                                    className={`w-16 h-16 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                                        step.number < currentStep
                                            ? 'bg-green-500 border-green-500 text-white'
                                            : step.number === currentStep
                                            ? 'bg-blue-500 border-blue-500 text-white'
                                            : 'bg-gray-100 border-gray-300 text-gray-400'
                                    }`}
                                >
                                    {step.number < currentStep ? (
                                        <CheckCircle size={24} />
                                    ) : (
                                        <step.icon size={24} />
                                    )}
                                </div>
                                <div className="mt-3 text-center">
                                    <p
                                        className={`text-sm font-medium ${
                                            step.number <= currentStep
                                                ? 'text-gray-900'
                                                : 'text-gray-400'
                                        }`}
                                    >
                                        Bước {step.number}
                                    </p>
                                    <p
                                        className={`text-lg ${
                                            step.number <= currentStep
                                                ? 'text-gray-600'
                                                : 'text-gray-400'
                                        }`}
                                    >
                                        {step.title}
                                    </p>
                                </div>
                            </div>
                            {index < steps.length - 1 && (
                                <div
                                    className={`w-24 h-0.5 mx-6 transition-all duration-300 ${
                                        step.number < currentStep
                                            ? 'bg-green-500'
                                            : 'bg-gray-300'
                                    }`}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ProgressBar;
