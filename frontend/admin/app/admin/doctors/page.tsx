'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import axiosInstance from '@/lib/axiosInstance';
import { Doctor } from '@/types';
import {
    Plus,
    Search,
    Edit,
    Trash2,
    Mail,
    Phone,
    UserCheck,
} from 'lucide-react';
import { useAppContext } from '@/app/context/AppContext';

export default function DoctorsPage() {
    const { userRole } = useAppContext();
    const [doctors, setDoctors] = useState<Doctor[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingDoctor, setEditingDoctor] = useState<Doctor | null>(null);
    const [formData, setFormData] = useState({
        id: 0,
        full_name: '',
        email: '',
        phone: '',
        specialty: '',
    });

    const hasFetched = useRef(false);

    useEffect(() => {
        if (userRole && !hasFetched.current) {
            fetchDoctors(userRole);
            hasFetched.current = true;
        }
    }, [userRole]);

    const fetchDoctors = async (role: string | null) => {
        try {
            const endpoint = role === 'doctor' ? '/doctors/me' : '/doctors/';
            const response = await axiosInstance.get(endpoint);

            const formattedDoctors =
                role === 'doctor'
                    ? [{ ...response.data, status: 'active' }]
                    : response.data.map((doctor: any) => ({
                          ...doctor,
                          status: 'active',
                      }));

            setDoctors(formattedDoctors);
        } catch (error) {
            console.error('Failed to fetch doctors:', error);
        } finally {
            setIsLoading(false);
        }
    };

    //Thêm và chỉnh sửa bác sĩ
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userRole) return;

        try {
            if (editingDoctor) {
                const endpoint =
                    userRole === 'doctor'
                        ? '/doctors/me'
                        : `/doctors/${editingDoctor.id}`;
                await axiosInstance.put(endpoint, formData);
            } else if (userRole === 'admin') {
                const { id, ...dataWithoutId } = formData;
                await axiosInstance.post('/doctors/', dataWithoutId);
            }
            setIsDialogOpen(false);
            setEditingDoctor(null);
            resetForm();
            fetchDoctors(userRole);
        } catch (error) {
            console.error('Failed to save doctor:', error);
        }
    };

    //Xóa bác sĩ
    const handleDelete = async (id: number) => {
        if (userRole !== 'admin') return;

        if (confirm('Bạn có chắc muốn xóa bác sĩ này không?')) {
            try {
                await axiosInstance.delete(`/doctors/${id}`);
                fetchDoctors(userRole);
            } catch (error) {
                console.error('Xóa bác sĩ thất bại:', error);
            }
        }
    };

    const resetForm = () => {
        setFormData({
            id: 0,
            full_name: '',
            email: '',
            phone: '',
            specialty: '',
        });
    };

    const openEditDialog = (doctor: Doctor) => {
        if (!userRole) return;

        setEditingDoctor(doctor);
        setFormData({
            id: doctor.id,
            full_name: doctor.full_name,
            email: doctor.email,
            phone: doctor.phone,
            specialty: doctor.specialty || '',
        });
        setIsDialogOpen(true);
    };

    const filteredDoctors = doctors.filter(
        doctor =>
            doctor.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (doctor.specialty?.toLowerCase() || '').includes(
                searchTerm.toLowerCase()
            )
    );

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
                title="Bác sĩ"
                description={
                    userRole === 'admin'
                        ? 'Quản lý nhân viên y tế và chuyên môn của họ'
                        : 'Thông tin cá nhân'
                }
            >
                {userRole === 'admin' && (
                    <Button
                        onClick={() => {
                            setEditingDoctor(null);
                            resetForm();
                            setIsDialogOpen(true);
                        }}
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Thêm bác sĩ
                    </Button>
                )}
            </PageHeader>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>
                            {editingDoctor
                                ? 'Chỉnh sửa bác sĩ'
                                : 'Thêm bác sĩ mới'}
                        </DialogTitle>
                        <DialogDescription>
                            {editingDoctor
                                ? 'Chỉnh sửa thông tin của bác sĩ được chọn.'
                                : 'Thêm bác sĩ mới vào hệ thống.'}
                        </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <Label htmlFor="id">ID</Label>
                            <Input
                                id="id"
                                type="number"
                                value={formData.id || ''}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        id: Number(e.target.value) || 0,
                                    })
                                }
                                disabled={!!editingDoctor}
                                required={!!editingDoctor}
                            />
                        </div>
                        <div>
                            <Label htmlFor="full_name">Họ và tên</Label>
                            <Input
                                id="full_name"
                                value={formData.full_name}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        full_name: e.target.value,
                                    })
                                }
                                required
                            />
                        </div>
                        <div>
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                value={formData.email}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        email: e.target.value,
                                    })
                                }
                                required
                            />
                        </div>
                        <div>
                            <Label htmlFor="phone">Số điện thoại</Label>
                            <Input
                                id="phone"
                                value={formData.phone}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        phone: e.target.value,
                                    })
                                }
                                required
                            />
                        </div>
                        <div>
                            <Label htmlFor="specialty">Chuyên môn</Label>
                            <Input
                                id="specialty"
                                value={formData.specialty}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        specialty: e.target.value,
                                    })
                                }
                                required
                            />
                        </div>
                        <div className="flex gap-2 pt-4">
                            <Button type="submit" className="flex-1">
                                {editingDoctor ? 'Cập nhật' : 'Tạo mới'}
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => setIsDialogOpen(false)}
                            >
                                Hủy
                            </Button>
                        </div>
                    </form>
                </DialogContent>
            </Dialog>

            {userRole === 'admin' && (
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                        placeholder="Tìm kiếm bác sĩ..."
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                        className="pl-10"
                    />
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredDoctors.map(doctor => (
                    <Card
                        key={doctor.id}
                        className="hover:shadow-lg transition-shadow"
                    >
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                        <UserCheck className="h-6 w-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">
                                            {doctor.full_name}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            {doctor.specialty || 'N/A'}
                                        </p>
                                    </div>
                                </div>
                                <Badge
                                    variant={
                                        doctor.status === 'active'
                                            ? 'default'
                                            : 'secondary'
                                    }
                                >
                                    {doctor.status}
                                </Badge>
                            </div>

                            <div className="space-y-2 mb-4">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Mail className="h-4 w-4" />
                                    {doctor.email}
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Phone className="h-4 w-4" />
                                    {doctor.phone}
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => openEditDialog(doctor)}
                                    className="flex-1"
                                >
                                    <Edit className="h-4 w-4 mr-1" />
                                    Sửa
                                </Button>
                                {userRole === 'admin' && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => handleDelete(doctor.id)}
                                        className="text-red-600 hover:text-red-700"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {filteredDoctors.length === 0 && (
                <div className="text-center py-12">
                    <UserCheck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Không tìm thấy bác sĩ
                    </h3>
                    <p className="text-gray-600">
                        {searchTerm
                            ? 'Thử điều chỉnh từ khóa tìm kiếm.'
                            : 'Bắt đầu bằng cách thêm bác sĩ đầu tiên.'}
                    </p>
                </div>
            )}
        </div>
    );
}
