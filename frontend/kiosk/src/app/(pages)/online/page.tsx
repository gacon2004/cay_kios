// src/app/(pages)/bhyt/page.tsx
import type { Metadata } from 'next';
import dynamic from 'next/dynamic';

// Dynamic import mà không vô hiệu hóa SSR
const BHYTFlow = dynamic(() => import('@/app/(pages)/offline/BHYTFlow'));

export const metadata: Metadata = {
    title: 'KIOSK - Đăng ký khám online',
    description: 'Quy trình đăng ký khám bảo hiểm y tế tại Kiosk',
};

export default function Page() {
    return <BHYTFlow />;
}
