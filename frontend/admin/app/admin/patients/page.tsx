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
      const response = await axiosInstance.get('/patients');
      setPatients(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      // Fallback data for demo
      setPatients([
        {
          id: '1',
          name: 'Nguyen Van A',
          email: 'nguyenvana@gmail.com',
          phone: '+84 901 234 567',
          cccd: '001234567890',
          dateOfBirth: '1985-06-15',
          gender: 'male',
          address: '123 Le Loi St, District 1, Ho Chi Minh City',
          createdAt: '2024-01-15T08:00:00Z',
        },
        {
          id: '2',
          name: 'Tran Thi B',
          email: 'tranthib@gmail.com',
          phone: '+84 902 345 678',
          cccd: '001234567891',
          dateOfBirth: '1990-03-22',
          gender: 'female',
          address: '456 Nguyen Hue St, District 1, Ho Chi Minh City',
          createdAt: '2024-01-10T08:00:00Z',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.cccd.includes(searchTerm) ||
    patient.phone.includes(searchTerm)
  );

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    const age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
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
        title="Patients"
        description="View and manage patient records"
      />

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          placeholder="Search by name, CCCD, or phone..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredPatients.map((patient) => (
          <Card key={patient.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <Users className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{patient.name}</h3>
                    <p className="text-sm text-gray-600">CCCD: {patient.cccd}</p>
                  </div>
                </div>
                <Badge variant="outline">
                  {calculateAge(patient.dateOfBirth)} years old
                </Badge>
              </div>
              
              <div className="space-y-2 mb-4">
                {patient.email && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="h-4 w-4" />
                    {patient.email}
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="h-4 w-4" />
                  {patient.phone}
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="h-4 w-4" />
                  Born: {new Date(patient.dateOfBirth).toLocaleDateString()}
                </div>
                <div className="flex items-start gap-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mt-0.5" />
                  <span className="line-clamp-2">{patient.address}</span>
                </div>
              </div>
              
              <div className="pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    Gender: <span className="capitalize text-gray-700">{patient.gender}</span>
                  </span>
                  <span className="text-gray-500">
                    Registered: {new Date(patient.createdAt).toLocaleDateString()}
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
          <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Try adjusting your search terms.' : 'No patients have been registered yet.'}
          </p>
        </div>
      )}
    </div>
  );
}