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
import axiosInstance from '@/lib/axiosInstance';
import { Room } from '@/types';
import { Plus, Search, Edit, Trash2, Building2 } from 'lucide-react';
import { useAppContext } from '@/app/context/AppContext';

export default function RoomsPage() {
    const { userRole } = useAppContext();
    const [rooms, setRooms] = useState<Room[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingRoom, setEditingRoom] = useState<Room | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        service_id: 0,
        location: '',
        status: 'Còn trống' as 'Còn trống' | 'Đã đầy' | 'Bảo trì',
    });

    const hasFetched = useRef(false);

    useEffect(() => {
        if (userRole && !hasFetched.current) {
            fetchRooms(userRole);
            hasFetched.current = true;
        }
    }, [userRole]);

    const fetchRooms = async (role: string | null) => {
        try {
            let endpoint = 'clinics/';
            if (role === 'doctor') {
                endpoint = `/clinics/doctor/me`
            }

            const response = await axiosInstance.get(endpoint);
            setRooms(response.data || []);
        } catch (error) {
            console.error('Failed to fetch rooms:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const payload = {
                name: formData.name,
                service_id: Number(formData.service_id),
                location: formData.location,
                status: formData.status,
            };

            if (editingRoom) {
                await axiosInstance.put(`/clinics/${editingRoom.id}`, payload);
            } else {
                await axiosInstance.post('/clinics', payload);
            }
            setIsDialogOpen(false);
            setEditingRoom(null);
            resetForm();
            fetchRooms(userRole);
        } catch (error) {
            console.error('Failed to save room:', error);
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm('Bạn có chắc chắn muốn xóa phòng này?')) {
            try {
                await axiosInstance.delete(`/clinics/${id}`);
                fetchRooms(userRole);
            } catch (error) {
                console.error('Failed to delete room:', error);
            }
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            service_id: 0,
            location: '',
            status: 'Còn trống',
        });
    };

    const openEditDialog = (room: Room) => {
        setEditingRoom(room);
        setFormData({
            name: room.name,
            service_id: room.service_id,
            location: room.location,
            status: room.status,
        });
        setIsDialogOpen(true);
    };

    const getStatusColor = (status: Room['status']) => {
        switch (status) {
            case 'Còn trống':
                return 'bg-green-100 text-green-800';
            case 'Đã đầy':
                return 'bg-red-100 text-red-800';
            case 'Bảo trì':
                return 'bg-yellow-100 text-yellow-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const filteredRooms = rooms.filter(room =>
        (room?.name ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (room?.location ?? '').toLowerCase().includes(searchTerm.toLowerCase())
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
                title="Phòng"
                description="Quản lý các phòng khám và thông tin chi tiết"
            >
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button
                            onClick={() => {
                                setEditingRoom(null);
                                resetForm();
                            }}
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Thêm phòng
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                        <DialogHeader>
                            <DialogTitle>
                                {editingRoom ? 'Sửa phòng' : 'Thêm phòng mới'}
                            </DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <Label htmlFor="name">Tên phòng</Label>
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
                                <Label htmlFor="service_id">ID Dịch vụ</Label>
                                <Input
                                    id="service_id"
                                    type="number"
                                    value={formData.service_id}
                                    onChange={e =>
                                        setFormData({
                                            ...formData,
                                            service_id: Number(e.target.value),
                                        })
                                    }
                                    required
                                />
                            </div>
                            <div>
                                <Label htmlFor="location">Vị trí</Label>
                                <Input
                                    id="location"
                                    value={formData.location}
                                    onChange={e =>
                                        setFormData({
                                            ...formData,
                                            location: e.target.value,
                                        })
                                    }
                                    required
                                />
                            </div>
                            <div>
                                <Label htmlFor="status">Trạng thái</Label>
                                <Select
                                    value={formData.status}
                                    onValueChange={(value: Room['status']) =>
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
                                        <SelectItem value="active">
                                            Còn trống
                                        </SelectItem>
                                        <SelectItem value="full">
                                            Đã đầy
                                        </SelectItem>
                                        <SelectItem value="fixed">
                                            Bảo trì
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="flex gap-2 pt-4">
                                <Button type="submit" className="flex-1">
                                    {editingRoom ? 'Cập nhật' : 'Tạo'}
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
            </PageHeader>

            {/* Search */}
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                    placeholder="Tìm kiếm phòng..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="pl-10"
                />
            </div>

            {/* Rooms Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRooms.map(room => (
                    <Card
                        key={room.id}
                        className="hover:shadow-lg transition-shadow"
                    >
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                                        <Building2 className="h-6 w-6 text-orange-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">
                                            {room.name}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            ID Dịch vụ: {room.service_id}
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            Vị trí: {room.location}
                                        </p>
                                    </div>
                                </div>
                                <Badge className={getStatusColor(room.status)}>
                                    {room.status}
                                </Badge>
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => openEditDialog(room)}
                                    className="flex-1"
                                >
                                    <Edit className="h-4 w-4 mr-1" />
                                    Sửa
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDelete(room.id)}
                                    className="text-red-600 hover:text-red-700"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {filteredRooms.length === 0 && (
                <div className="text-center py-12">
                    <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Không tìm thấy phòng
                    </h3>
                    <p className="text-gray-600">
                        {searchTerm
                            ? 'Hãy thử điều chỉnh từ khóa tìm kiếm.'
                            : 'Bắt đầu bằng cách thêm phòng đầu tiên.'}
                    </p>
                </div>
            )}
        </div>
    );
}
