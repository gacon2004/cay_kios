'use client';

import { Heart, CreditCard, Clock, FileText, ChevronRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/app/components/ui/use-toast';

export default function MainLayout() {
    const router = useRouter();
    const { toast } = useToast();

    const menuItems = [
        {
            id: 'bhyt',
            title: 'Khám Có BHYT',
            subtitle: 'Đăng ký khám bệnh với thẻ BHYT',
            icon: Heart,
            color: 'bg-blue-500',
            action: () => router.push('/offline'),
        },
        {
            id: 'service',
            title: 'Khám Dịch Vụ',
            subtitle: 'Đăng ký khám dịch vụ không BHYT',
            icon: CreditCard,
            color: 'bg-green-500',
            action: () => router.push('/offline'),
        },
        {
            id: 'appointment',
            title: 'Đặt Lịch Hẹn',
            subtitle: 'Đặt lịch khám theo thời gian',
            icon: Clock,
            color: 'bg-purple-500',
            action: () => router.push('/online'),
        },
        {
            id: 'results',
            title: 'Tra Cứu Kết Quả',
            subtitle: 'Xem kết quả khám bệnh',
            icon: FileText,
            color: 'bg-orange-500',
            action: () => router.push('/checkAppointments'),
        },
    ];

    return (
        <div className="min-h-[calc(100vh-4rem)] bg-background-secondary ">
            {/* Header */}
            <header className="w-full text-4xl px-5 py-[17px] bg-background text-center text-text">
                <h1 className="font-bold mb-4">Hệ Thống Đăng Ký Khám Bệnh</h1>
                <p className="text-[20px] mb-4">
                    Chọn loại dịch vụ bạn muốn sử dụng
                </p>
            </header>

            {/* Main Content */}
            <div className="flex-1 max-w-5xl mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {menuItems.map(item => (
                        <button
                            key={item.id}
                            onClick={item.action}
                            className="group relative bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 text-left border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1 cursor-pointer"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-6">
                                    <div
                                        className={`${item.color} rounded-xl p-4 text-white group-hover:scale-110 transition-transform duration-300`}
                                    >
                                        <item.icon size={32} />
                                    </div>
                                    <div>
                                        <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                                            {item.title}
                                        </h3>
                                        <p className="text-gray-600 text-sm">
                                            {item.subtitle}
                                        </p>
                                    </div>
                                </div>
                                <ChevronRight
                                    className="text-gray-400 group-hover:text-blue-500 transition-colors duration-300"
                                    size={28}
                                />
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full p-8 bg-background text-center text-text fixed bottom-0">
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
}
