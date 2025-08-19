'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useAuthStore } from '@/store/authStore';
import axiosInstance from '@/lib/axiosInstance';
import { User, Lock, LogOut, Bell, Shield, Database } from 'lucide-react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export default function SettingsPage() {
    const { user, logout } = useAuthStore();
    const router = useRouter();
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
    });

    const handleLogout = () => {
        logout();
        router.push('/admin/login');
    };

    const handlePasswordChange = async (e: React.FormEvent) => {
        e.preventDefault();

        if (passwordData.newPassword !== passwordData.confirmPassword) {
            alert('New passwords do not match');
            return;
        }

        setIsChangingPassword(true);
        try {
            await axiosInstance.post('/auth/change-password', {
                currentPassword: passwordData.currentPassword,
                newPassword: passwordData.newPassword,
            });

            alert('Password changed successfully');
            setPasswordData({
                currentPassword: '',
                newPassword: '',
                confirmPassword: '',
            });
        } catch (error) {
            console.error('Failed to change password:', error);
            alert('Failed to change password. Please try again.');
        } finally {
            setIsChangingPassword(false);
        }
    };

    return (
        <div className="space-y-8">
            <PageHeader
                title="Settings"
                description="Manage your account settings and system preferences"
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Profile Section */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <User className="h-5 w-5" />
                                Profile Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="name">Full Name</Label>
                                    <Input
                                        id="name"
                                        value={user?.name || ''}
                                        disabled
                                        className="bg-gray-50"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input
                                        id="email"
                                        value={user?.email || ''}
                                        disabled
                                        className="bg-gray-50"
                                    />
                                </div>
                            </div>
                            <div>
                                <Label htmlFor="role">Role</Label>
                                <Input
                                    id="role"
                                    value={user?.role || 'Administrator'}
                                    disabled
                                    className="bg-gray-50"
                                />
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Lock className="h-5 w-5" />
                                Change Password
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form
                                onSubmit={handlePasswordChange}
                                className="space-y-4"
                            >
                                <div>
                                    <Label htmlFor="currentPassword">
                                        Current Password
                                    </Label>
                                    <Input
                                        id="currentPassword"
                                        type="password"
                                        value={passwordData.currentPassword}
                                        onChange={e =>
                                            setPasswordData({
                                                ...passwordData,
                                                currentPassword: e.target.value,
                                            })
                                        }
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="newPassword">
                                        New Password
                                    </Label>
                                    <Input
                                        id="newPassword"
                                        type="password"
                                        value={passwordData.newPassword}
                                        onChange={e =>
                                            setPasswordData({
                                                ...passwordData,
                                                newPassword: e.target.value,
                                            })
                                        }
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="confirmPassword">
                                        Confirm New Password
                                    </Label>
                                    <Input
                                        id="confirmPassword"
                                        type="password"
                                        value={passwordData.confirmPassword}
                                        onChange={e =>
                                            setPasswordData({
                                                ...passwordData,
                                                confirmPassword: e.target.value,
                                            })
                                        }
                                        required
                                    />
                                </div>
                                <Button
                                    type="submit"
                                    disabled={isChangingPassword}
                                >
                                    {isChangingPassword ? (
                                        <>
                                            <LoadingSpinner
                                                size="sm"
                                                className="mr-2"
                                            />
                                            Changing Password...
                                        </>
                                    ) : (
                                        'Change Password'
                                    )}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Bell className="h-5 w-5" />
                                Notification Preferences
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium">
                                        Email Notifications
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Receive notifications via email
                                    </p>
                                </div>
                                <Button variant="outline" size="sm">
                                    Configure
                                </Button>
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium">System Alerts</p>
                                    <p className="text-sm text-gray-600">
                                        Get notified about system issues
                                    </p>
                                </div>
                                <Button variant="outline" size="sm">
                                    Configure
                                </Button>
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium">Daily Reports</p>
                                    <p className="text-sm text-gray-600">
                                        Receive daily statistics reports
                                    </p>
                                </div>
                                <Button variant="outline" size="sm">
                                    Configure
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* System Information Sidebar */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Shield className="h-5 w-5" />
                                Security
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="text-sm">
                                <p className="font-medium text-green-600">
                                    Security Status: Strong
                                </p>
                                <p className="text-gray-600 mt-1">
                                    Last login: Today at 9:15 AM
                                </p>
                            </div>
                            <Separator />
                            <div className="space-y-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="w-full justify-start"
                                >
                                    View Login History
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="w-full justify-start"
                                >
                                    Manage Sessions
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Database className="h-5 w-5" />
                                System Status
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-600">
                                        Database
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                        <span className="text-sm font-medium">
                                            Online
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-600">
                                        API Server
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                        <span className="text-sm font-medium">
                                            Healthy
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-600">
                                        Kiosk Connection
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                        <span className="text-sm font-medium">
                                            Active
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <Separator />
                            <div className="text-xs text-gray-500">
                                <p>Version: 1.0.0</p>
                                <p>Last Update: Jan 15, 2024</p>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">
                                Account Actions
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button
                                variant="outline"
                                onClick={handleLogout}
                                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                                <LogOut className="h-4 w-4 mr-2" />
                                Sign Out
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
