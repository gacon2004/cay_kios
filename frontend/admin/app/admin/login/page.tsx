'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import axiosInstance from '@/lib/axiosInstance';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
} from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Stethoscope, AlertCircle, Eye, EyeOff } from 'lucide-react';
import Link from 'next/link';
import { useAppContext } from '@/app/context/AppContext';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false); // State mới để quản lý hiển thị mật khẩu
    const { login, isAuthenticated, initializeAuth } = useAuthStore();
    const { setUserRole } = useAppContext();
    const router = useRouter();

    useEffect(() => {
        // Khởi tạo trạng thái xác thực khi tải trang
        initializeAuth();
    }, [initializeAuth]);

    useEffect(() => {
        // Nếu đã xác thực, chuyển hướng ngay lập tức
        if (isAuthenticated) {
            router.push('/admin/dashboard');
        }
    }, [isAuthenticated, router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await axiosInstance.post('/auth/signin', {
                username,
                password,
            });
            const { user, token } = response.data;
            const userData = {
                id: user.id,
                name: user.full_name,
                role: user.role,
            };

            // Lưu vào localStorage
            localStorage.setItem('user', JSON.stringify(userData));
            localStorage.setItem('token', token.access_token);

            // Cập nhật trạng thái xác thực
            login(userData, token.access_token);

            // Cập nhật userRole
            setUserRole(userData.role);

            // Chuyển hướng
            router.push('/admin/dashboard');
        } catch (error: any) {
            setError(
                error.response?.data?.message ||
                    'Đăng nhập thất bại. Vui lòng thử lại.'
            );
            setIsLoading(false);
        }
    };

    const handleRegisterRedirect = () => {
        router.push('/admin/register');
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword); // Chuyển đổi trạng thái hiển thị mật khẩu
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
                            <Stethoscope className="h-7 w-7 text-white" />
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold">
                        MedKiosk Admin
                    </CardTitle>
                    <CardDescription>
                        Đăng nhập để truy cập bảng điều khiển quản trị
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="flex items-center gap-2 p-3 text-sm text-red-700 bg-red-50 rounded-lg">
                                <AlertCircle className="h-4 w-4" />
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="username">Tên đăng nhập</Label>
                            <Input
                                id="username"
                                type="text"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                placeholder="admin"
                                required
                                disabled={isLoading}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Mật khẩu</Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'} // Chuyển đổi type dựa trên trạng thái
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="Nhập mật khẩu của bạn"
                                    required
                                    disabled={isLoading}
                                />
                                <button
                                    type="button"
                                    onClick={togglePasswordVisibility}
                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5" />
                                    ) : (
                                        <Eye className="h-5 w-5" />
                                    )}
                                </button>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <LoadingSpinner
                                        size="sm"
                                        className="mr-2"
                                    />
                                    Đang đăng nhập...
                                </>
                            ) : (
                                'Đăng Nhập'
                            )}
                        </Button>

                        <Button
                            type="button"
                            variant="outline"
                            className="w-full mt-2"
                            onClick={handleRegisterRedirect}
                            disabled={isLoading}
                        >
                            Đăng Ký
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
