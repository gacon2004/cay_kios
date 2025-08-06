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
      const response = await axiosInstance.get('/appointments');
      setAppointments(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
      // Fallback data for demo
      setAppointments([
        {
          id: '1',
          patientId: '1',
          doctorId: '1',
          serviceId: '1',
          roomId: '1',
          patient: {
            id: '1',
            name: 'Nguyen Van A',
            phone: '+84 901 234 567',
            cccd: '001234567890',
            dateOfBirth: '1985-06-15',
            gender: 'male',
            address: '123 Le Loi St, District 1, Ho Chi Minh City',
            createdAt: '2024-01-15T08:00:00Z',
          },
          doctor: {
            id: '1',
            name: 'Dr. Sarah Johnson',
            email: 'sarah.johnson@medkiosk.com',
            phone: '+84 901 234 567',
            specialization: 'Cardiology',
            status: 'active',
            createdAt: '2024-01-15T08:00:00Z',
          },
          service: {
            id: '1',
            name: 'General Checkup',
            description: 'Comprehensive health examination',
            price: 500000,
            duration: 30,
            status: 'active',
            createdAt: '2024-01-15T08:00:00Z',
          },
          room: {
            id: '1',
            name: 'Examination Room 1',
            type: 'General',
            status: 'available',
            equipment: ['Examination table', 'Blood pressure monitor'],
            createdAt: '2024-01-15T08:00:00Z',
          },
          scheduledAt: '2024-01-20T09:00:00Z',
          status: 'scheduled',
          notes: 'Annual health checkup',
          createdAt: '2024-01-15T08:00:00Z',
        },
        {
          id: '2',
          patientId: '2',
          doctorId: '2',
          serviceId: '2',
          roomId: '3',
          patient: {
            id: '2',
            name: 'Tran Thi B',
            phone: '+84 902 345 678',
            cccd: '001234567891',
            dateOfBirth: '1990-03-22',
            gender: 'female',
            address: '456 Nguyen Hue St, District 1, Ho Chi Minh City',
            createdAt: '2024-01-10T08:00:00Z',
          },
          doctor: {
            id: '2',
            name: 'Dr. Michael Chen',
            email: 'michael.chen@medkiosk.com',
            phone: '+84 902 345 678',
            specialization: 'General Medicine',
            status: 'active',
            createdAt: '2024-01-10T08:00:00Z',
          },
          service: {
            id: '2',
            name: 'Blood Test',
            description: 'Complete blood count',
            price: 200000,
            duration: 15,
            status: 'active',
            createdAt: '2024-01-10T08:00:00Z',
          },
          room: {
            id: '3',
            name: 'Laboratory',
            type: 'Lab',
            status: 'available',
            equipment: ['Microscope', 'Centrifuge'],
            createdAt: '2024-01-08T08:00:00Z',
          },
          scheduledAt: '2024-01-20T10:30:00Z',
          status: 'completed',
          createdAt: '2024-01-10T08:00:00Z',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: Appointment['status']) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAppointments = appointments.filter(appointment => {
    const matchesSearch = 
      appointment.patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.doctor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      appointment.service.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || appointment.status === statusFilter;
    
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
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="scheduled">Scheduled</SelectItem>
            <SelectItem value="in-progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Appointments List */}
      <div className="space-y-4">
        {filteredAppointments.map((appointment) => (
          <Card key={appointment.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg text-gray-900">
                      {appointment.service.name}
                    </h3>
                    <Badge className={getStatusColor(appointment.status)}>
                      {appointment.status.replace('-', ' ')}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.patient.name}</p>
                        <p className="text-gray-600">{appointment.patient.phone}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <UserCheck className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.doctor.name}</p>
                        <p className="text-gray-600">{appointment.doctor.specialization}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">
                          {new Date(appointment.scheduledAt).toLocaleDateString()}
                        </p>
                        <p className="text-gray-600">
                          {new Date(appointment.scheduledAt).toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium">{appointment.room.name}</p>
                        <p className="text-gray-600">{appointment.room.type}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {appointment.service.duration} min
                      </div>
                      <div className="font-medium text-green-600">
                        ₫{appointment.service.price.toLocaleString()}
                      </div>
                    </div>
                    
                    {appointment.notes && (
                      <p className="text-sm text-gray-600 italic max-w-xs truncate">
                        {appointment.notes}
                      </p>
                    )}
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