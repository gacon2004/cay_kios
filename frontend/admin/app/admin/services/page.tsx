'use client';

import { useEffect, useState, useRef } from 'react';
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
    DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import axiosInstance from '@/lib/axiosInstance';
import { Service } from '@/types';
import {
    Plus,
    Search,
    Edit,
    Trash2,
    Stethoscope,
    Clock,
    DollarSign,
} from 'lucide-react';
import { useAppContext } from '@/app/context/AppContext';

export default function ServicesPage() {
    const { userRole } = useAppContext();
    const [services, setServices] = useState<Service[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingService, setEditingService] = useState<Service | null>(null);
    const [formData, setFormData] = useState({
        id: 0,
        name: '',
        description: '',
        price: 0,
        duration: 0,
        status: 'active' as 'active' | 'inactive',
    });

    const hasFetched = useRef(false);

    useEffect(() => {
        if (userRole && !hasFetched.current) {
            fetchServices(userRole);
            hasFetched.current = true;
        }
    }, [userRole]);

    const fetchServices = async (role: string | null) => {
        try {
            let endpoint = '/services/';
            if (role === 'doctor') {
                const infoDoctor = await axiosInstance.get('/doctors/me');
                endpoint = `/services/${infoDoctor.data.specialty}`;
            }
            const response = await axiosInstance.get(endpoint);

            // Định dạng dữ liệu dịch vụ
            const formattedServices =
                role === 'doctor'
                    ? [{ ...response.data, status: 'active' }]
                    : response.data.map((service: any) => ({
                          ...service,
                          status: 'active',
                      }));

            // Xác thực dữ liệu với kiểu Service
            const validServices = formattedServices.filter(
                (item: any) =>
                    item &&
                    typeof item === 'object' &&
                    'id' in item &&
                    'name' in item
            );

            setServices(validServices);
        } catch (error: any) {
            console.error('Lấy dịch vụ thất bại:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
            });
            setServices([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                price: Number(formData.price),
                duration: Number(formData.duration),
            };

            if (editingService) {
                await axiosInstance.put(
                    `/services/${editingService.id}`,
                    payload
                );
            } else {
                await axiosInstance.post('/services', payload);
            }
            setIsDialogOpen(false);
            setEditingService(null);
            resetForm();
            fetchServices(userRole);
        } catch (error) {
            console.error('Lưu dịch vụ thất bại:', error); // Ghi log lỗi
        }
    };

    const handleDelete = async (id: string) => {
        if (confirm('Bạn có chắc chắn muốn xóa dịch vụ này?')) {
            try {
                await axiosInstance.delete(`/services/${id}`);
                fetchServices(userRole);
            } catch (error) {
                console.error('Xóa dịch vụ thất bại:', error); // Ghi log lỗi
            }
        }
    };

    const resetForm = () => {
        setFormData({
            id: 0,
            name: '',
            description: '',
            price: 0,
            duration: 0,
            status: 'active',
        });
    };

    const openEditDialog = (service: Service) => {
        setEditingService(service);
        setFormData({
            id: service.id ? Number(service.id) : 0,
            name: service.name || '',
            description: service.description || '',
            price: service.price || 0,
            duration: service.duration || 0,
            status: service.status || 'active',
        });
        setIsDialogOpen(true);
    };

    // Logic lọc dữ liệu dịch vụ
    const filteredServices = Array.isArray(services)
        ? services.filter(
              service =>
                  (service.name?.toLowerCase() || '').includes(
                      searchTerm.toLowerCase()
                  ) ||
                  (service.description?.toLowerCase() || '').includes(
                      searchTerm.toLowerCase()
                  )
          )
        : [];

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <PageHeader title="Dịch vụ" description="Quản lý dịch vụ và giá cả">
                {userRole === 'admin' && (
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button
                        onClick={() => {
                            setEditingService(null);
                            resetForm();
                        }}
                        >
                        <Plus className="h-4 w-4 mr-2" />
                        Thêm Dịch Vụ
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                        <DialogHeader>
                        <DialogTitle>
                            {editingService ? 'Sửa Dịch Vụ' : 'Thêm Dịch Vụ'}
                        </DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <Label htmlFor="name">Tên Dịch Vụ</Label>
                            <Input
                            id="name"
                            value={formData.name}
                            onChange={e =>
                                setFormData({
                                ...formData,
                                name: e.target.value,
                                })
                            }
                            required
                            />
                        </div>
                        <div>
                            <Label htmlFor="description">Mô Tả</Label>
                            <Textarea
                            id="description"
                            value={formData.description}
                            onChange={e =>
                                setFormData({
                                ...formData,
                                description: e.target.value,
                                })
                            }
                            rows={3}
                            required
                            />
                        </div>
                        <div>
                            <Label htmlFor="price">Giá (VND)</Label>
                            <Input
                            id="price"
                            type="number"
                            value={formData.price}
                            onChange={e =>
                                setFormData({
                                ...formData,
                                price: Number(e.target.value),
                                })
                            }
                            required
                            />
                        </div>
                        <div>
                            <Label htmlFor="duration">Thời gian dự kiến (phút)</Label>
                            <Input
                            id="duration"
                            type="number"
                            value={formData.duration}
                            onChange={e =>
                                setFormData({
                                ...formData,
                                duration: Number(e.target.value),
                                })
                            }
                            required
                            />
                        </div>
                        <div>
                            <Label htmlFor="status">Trạng Thái</Label>
                            <Select
                            value={formData.status}
                            onValueChange={(value: 'active' | 'inactive') =>
                                setFormData({
                                ...formData,
                                status: value,
                                })
                            }
                            >
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="active">Hoạt động</SelectItem>
                                <SelectItem value="inactive">Ngừng hoạt động</SelectItem>
                            </SelectContent>
                            </Select>
                        </div>
                        <div className="flex gap-2 pt-4">
                            <Button type="submit" className="flex-1">
                            {editingService ? 'Sửa' : 'Tạo mới'}
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
                )}
            </PageHeader>

            {/* Tìm kiếm */}
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                    placeholder="Tìm kiếm dịch vụ..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="pl-10"
                />
            </div>

            {/* Lưới dịch vụ */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredServices.map(service => (
                    <Card
                        key={service.id}
                        className="hover:shadow-lg transition-shadow"
                    >
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                                        <Stethoscope className="h-6 w-6 text-purple-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">
                                            {service.name || 'Không có tên'}
                                        </h3>
                                        <Badge
                                            variant={
                                                service.status === 'active'
                                                    ? 'default'
                                                    : 'secondary'
                                            }
                                        >
                                            <p>{service.id}</p>
                                            <p>{service.status}</p>
                                            
                                        </Badge>
                                    </div>
                                </div>
                            </div>

                            <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                                {service.description || 'Không có mô tả'}
                            </p>

                            <div className="space-y-2 mb-4">
                                <div className="flex items-center gap-2 text-sm">
                                    <span className="font-medium text-green-600">
                                        ₫{(service.price || 0).toLocaleString()}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Clock className="h-4 w-4" />
                                    {service.duration
                                        ? service.duration
                                        : '30'}{' '}
                                    phút
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => openEditDialog(service)}
                                    className="flex-1"
                                >
                                    <Edit className="h-4 w-4 mr-1" />
                                    Sửa
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDelete(service.id)}
                                    className="text-red-600 hover:text-red-700"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {filteredServices.length === 0 && (
                <div className="text-center py-12">
                    <Stethoscope className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Không tìm thấy dịch vụ
                    </h3>
                    <p className="text-gray-600">
                        {searchTerm
                            ? 'Thử điều chỉnh từ khóa tìm kiếm.'
                            : 'Bắt đầu bằng cách thêm dịch vụ đầu tiên.'}
                    </p>
                </div>
            )}
        </div>
    );
}
