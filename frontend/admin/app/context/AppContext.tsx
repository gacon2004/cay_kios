'use client';

import { useRouter } from 'next/navigation';
import {
    createContext,
    useContext,
    useState,
    useEffect,
    ReactNode,
} from 'react';
import { useAuthStore } from '@/store/authStore';

interface User {
    id: string;
    name: string;
    role: string;
}

interface AppContextType {
    userRole: string | null;
    setUserRole: (role: string | null) => void;
}

export type { User };

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useAppContext() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
}

export function AppProvider({ children }: { children: ReactNode }) {
    const router = useRouter();
    const [userRole, setUserRole] = useState<string | null>(null);
    const { user, initializeAuth, isAuthenticated, isLoading } = useAuthStore();

    useEffect(() => {
        // Chỉ khởi tạo auth một lần khi tải trang
        initializeAuth();
    }, [initializeAuth]);

    useEffect(() => {
        // Đồng bộ userRole khi trạng thái xác thực thay đổi
        if (!isLoading && isAuthenticated && user) {
            setUserRole(user.role || null);
        } else if (!isLoading && !isAuthenticated) {
            setUserRole(null);
            // Điều hướng về trang đăng nhập nếu chưa xác thực
            router.push('/admin/login');
        }
    }, [user, isAuthenticated, isLoading, router]);

    return (
        <AppContext.Provider
            value={{
                userRole,
                setUserRole,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}
