'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import MainLayout from './(pages)/main/page';

export default function Home() {
    const pathname = usePathname();
    const router = useRouter();

    useEffect(() => {
        let inactivityTimer: NodeJS.Timeout;

        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            if (pathname !== '/') {
                inactivityTimer = setTimeout(() => {
                    router.push('/');
                }, 45000); // sau 45 giây không tương tác
            }
        };

        //Check tương tác
        const handleActivity = () => {
            resetTimer();
        };

        window.addEventListener('click', handleActivity);
        window.addEventListener('touchstart', handleActivity);
        window.addEventListener('keydown', handleActivity);

        resetTimer(); // khởi tạo timer

        return () => {
            clearTimeout(inactivityTimer);
            window.removeEventListener('click', handleActivity);
            window.removeEventListener('touchstart', handleActivity);
            window.removeEventListener('keydown', handleActivity);
        };
    }, [pathname, router]);

    return <MainLayout />;
}
