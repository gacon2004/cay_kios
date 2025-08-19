'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import axiosInstance from '@/lib/axiosInstance';
import { Patient } from '@/types';
import { Search, Users, Mail, Phone, MapPin, Calendar } from 'lucide-react';

export default function PatientsPage() {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchPatients();
    }, []);

    const fetchPatients = async () => {
        try {
            const response = await axiosInstance.get('patients/');

            const validPatients = response.data || [];

            setPatients(validPatients);
        } catch (error) {
            console.error('Failed to fetch patients:', error);
            setPatients([]); // Đặt mảng rỗng nếu có lỗi
        } finally {
            setIsLoading(false);
        }
    };

    const filteredPatients = patients.filter(
        patient =>
            (patient.full_name?.toLowerCase() || '').includes(
                searchTerm.toLowerCase()
            ) ||
            (patient.national_id || '').includes(searchTerm) ||
            (patient.phone || '').includes(searchTerm)
    );

    const calculateAge = (dateOfBirth: string | undefined) => {
        if (!dateOfBirth) return 0; // Trả về 0 nếu dateOfBirth không hợp lệ
        const today = new Date();
        const birthDate = new Date(dateOfBirth);
        if (isNaN(birthDate.getTime())) return 0; // Kiểm tra ngày sinh hợp lệ
        const age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();

        if (
            monthDiff < 0 ||
            (monthDiff === 0 && today.getDate() < birthDate.getDate())
        ) {
            return age - 1;
        }
        return age;
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <PageHeader
                title="Bệnh nhân"
                description="Xem và quản lý hồ sơ bệnh nhân"
            />

            {/* Search */}
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                    placeholder="Tìm kiếm theo tên, CCCD, hoặc số điện thoại..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="pl-10"
                />
            </div>

            {/* Patients Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredPatients.map(patient => (
                    <Card
                        key={patient.id}
                        className="hover:shadow-lg transition-shadow"
                    >
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                        <Users className="h-6 w-6 text-green-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">
                                            {patient.full_name ||
                                                'Không có tên'}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            CCCD: {patient.national_id || 'N/A'}
                                        </p>
                                    </div>
                                </div>
                                <Badge variant="outline">
                                    {calculateAge(patient.date_of_birth)} tuổi
                                </Badge>
                            </div>

                            <div className="space-y-2 mb-4">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Phone className="h-4 w-4" />
                                    {patient.phone || 'N/A'}
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Calendar className="h-4 w-4" />
                                    Ngày sinh:{' '}
                                    {patient.date_of_birth
                                        ? new Date(
                                              patient.date_of_birth
                                          ).toLocaleDateString()
                                        : 'N/A'}
                                </div>
                                <div className="flex items-start gap-2 text-sm text-gray-600">
                                    <MapPin className="h-4 w-4 mt-0.5" />
                                    <span className="line-clamp-2">
                                        {patient.ward || 'N/A'} -{' '}
                                        {patient.district || 'N/A'} -{' '}
                                        {patient.province || 'N/A'}
                                    </span>
                                </div>
                            </div>

                            <div className="pt-2 border-t border-gray-100">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-gray-500">
                                        Giới tính:{' '}
                                        <span className="capitalize text-gray-700">
                                            {patient.gender || 'N/A'}
                                        </span>
                                    </span>
                                    <span className="text-gray-500">
                                        Ngày đăng ký:{' '}
                                        {patient.created_at
                                            ? new Date(
                                                  patient.created_at
                                              ).toLocaleDateString()
                                            : 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {filteredPatients.length === 0 && (
                <div className="text-center py-12">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Không tìm thấy bệnh nhân
                    </h3>
                    <p className="text-gray-600">
                        {searchTerm
                            ? 'Thử điều chỉnh từ khóa tìm kiếm.'
                            : 'Chưa có bệnh nhân nào được đăng ký.'}
                    </p>
                </div>
            )}
        </div>
    );
}
