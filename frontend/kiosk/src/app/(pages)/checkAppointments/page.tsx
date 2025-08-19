import type { Metadata } from 'next';
import dynamic from 'next/dynamic';

const CheckFlow = dynamic(() => import('./CheckFlow'));

export const metadata: Metadata = {
    title: 'KIOSK - Kiểm tra lịch hẹn',
    description: 'Kiểm tra lịch hẹn tại Kiosk',
};

export default function Page() {
    return <CheckFlow />;
}
