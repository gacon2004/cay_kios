'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import axiosInstance from '@/lib/axiosInstance';
import { Appointment } from '@/types';
import { Search, Calendar, Clock, User, UserCheck, Building2, Eye } from 'lucide-react';

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await axiosInstance.get('/appointments/admin/payment');
      setAppointments(response.data || []);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
      // Fallback data for demo
    
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: Appointment['pay_status']) => {
    switch (status) {
      case 'AWAITING': return 'bg-yellow-100 text-yellow-800';
      case 'PAID': return 'bg-green-100 text-green-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAppointments = appointments.filter(appointment => {
    const matchesSearch = 
      appointment.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.estimated_time &&
      appointment.estimated_time.toString().toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.patient_dob.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.patient_gender.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.patient_national_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.patient_phone.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.pay_status.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.doctor_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.clinic_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || appointment.pay_status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

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
        title="Appointments"
        description="View and manage all appointment records"
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search appointments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tất cả</SelectItem>
            <SelectItem value="AWAITING">Đang chờ</SelectItem>
            <SelectItem value="PAID">Thành công</SelectItem>
            <SelectItem value="CANCELLED">Đã hủy</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Appointments List */}
      <div className="space-y-4">
        {filteredAppointments.map((appointment) => (
          <Card key={appointment.appointment_id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg text-gray-900">
                      {appointment.clinic_name} - {appointment.doctor_name}
                    </h3>
                    <Badge className={getStatusColor(appointment.pay_status)}>
                      {appointment.pay_status.replace('-', ' ')==='AWAITING' ? 'Đang chờ' : appointment.pay_status==='PAID' ? 'Thành công' : 'Đã hủy'}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.patient_name}</p>
                        <p className="font-medium">{appointment.patient_dob}</p>
                        <p className="font-medium">{appointment.patient_gender}</p>
                        <p className="text-gray-600">{appointment.patient_phone}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <UserCheck className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.doctor_name}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        {appointment.paid_at ? (
                          <p className="font-medium text-green-600">Hoàn thành</p>
                        ) : (
                          <p className="font-medium text-yellow-600">Đang chờ</p>
                        )}
                        <p className="text-gray-600">
                          {new Date(appointment.estimated_time).toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.clinic_name}</p>
                        
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        30 min
                      </div>
                      <div className="font-medium text-green-600">
                        ₫{appointment.price_vnd.toLocaleString()}
                      </div>
                    </div>
                      <p className="text-sm text-gray-600 italic max-w-xs truncate">
                          Vui lòng đến trước 15 phút để làm thủ tục
                      </p>
                  </div>
                </div>
                
                <div className="flex lg:flex-col gap-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAppointments.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No appointments found</h3>
          <p className="text-gray-600">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search terms or filters.' 
              : 'No appointments have been scheduled yet.'
            }
          </p>
        </div>
      )}
    </div>
  );
}