'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination';
import axiosInstance from '@/lib/axiosInstance';
import { Patient } from '@/types';
import { Search, Users, Phone, MapPin, Calendar, X } from 'lucide-react';

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Gọi API
  const fetchPatients = async (page: number, limit: number, search: string = '') => {
    setIsLoading(true);
    try {
      const offset = (page - 1) * limit;
      let url = `patients/?limit=${limit}&offset=${offset}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }
      const response = await axiosInstance.get(url);

      setPatients(response.data.data || []);

      // ✅ Lấy pagination đúng chỗ
      const pagination = response.data.pagination || {};
      setTotalPages(pagination.totalPages || 1);
      setTotalRecords(pagination.totalRecords || 0);
      setCurrentPage(pagination.page || page);
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      setPatients([]);
      setTotalPages(1);
      setTotalRecords(0);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients(currentPage, pageSize, searchTerm);
  }, [currentPage, pageSize]);

  const calculateAge = (dateOfBirth: string | undefined) => {
    if (!dateOfBirth) return 0;
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    if (isNaN(birthDate.getTime())) return 0;
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchPatients(1, pageSize, searchTerm);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setCurrentPage(1);
    fetchPatients(1, pageSize, '');
  };

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSize = Number(e.target.value);
    setPageSize(newSize);
    setCurrentPage(1);
    fetchPatients(1, newSize, searchTerm);
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
      <PageHeader title="Bệnh nhân" description="Xem và quản lý hồ sơ bệnh nhân" />

      {/* Search */}
      <div className="relative max-w-md flex">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 cursor-pointer hover:text-black"
          onClick={handleSearch}
          role="button"
          tabIndex={0}
        />
        <Input
            placeholder="Tìm kiếm theo tên, CCCD, hoặc số điện thoại..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            onKeyDown={e => {
                if (e.key === 'Enter') {
                handleSearch();
                }
            }}
            className="pl-10 pr-10"
        />

        {searchTerm && (
          <X
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 cursor-pointer hover:text-black"
            onClick={handleClearSearch}
            role="button"
            tabIndex={0}
          />
        )}
      </div>

      {/* Chọn số bản ghi mỗi trang */}
      <div className="flex items-center gap-3">
        <label className="text-sm text-gray-700">Số bản ghi mỗi trang:</label>
        <select
          value={pageSize}
          onChange={handlePageSizeChange}
          className="border rounded-md px-2 py-1 text-sm"
        >
          {[10, 15, 20, 25].map(size => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>

      {/* Hiển thị số kết quả */}
      <p className="text-sm text-gray-600">
        Tìm thấy <b>{totalRecords}</b> kết quả — Trang {currentPage}/{totalPages}
      </p>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {patients.map(patient => (
          <Card key={patient.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <Users className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {patient.full_name || 'Không có tên'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      CCCD: {patient.national_id || 'N/A'}
                    </p>
                  </div>
                </div>
                <Badge variant="outline">{calculateAge(patient.date_of_birth)} tuổi</Badge>
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
                    ? new Date(patient.date_of_birth).toLocaleDateString('vi-VN')
                    : 'N/A'}
                </div>
                <div className="flex items-start gap-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mt-0.5" />
                  <span className="line-clamp-2">
                    {patient.ward || 'N/A'} - {patient.district || 'N/A'} - {patient.province || 'N/A'}
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    Giới tính: <span className="capitalize text-gray-700">{patient.gender || 'N/A'}</span>
                  </span>
                  <span className="text-gray-500">
                    Ngày đăng ký:{' '}
                    {patient.created_at ? new Date(patient.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {patients.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Không tìm thấy bệnh nhân</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Thử điều chỉnh từ khóa tìm kiếm.' : 'Chưa có bệnh nhân nào được đăng ký.'}
          </p>
        </div>
      )}

      {/* Pagination */}
      <div className="flex justify-center mt-8">
        <Pagination className="w-full max-w-md">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                href="#"
                onClick={e => {
                  e.preventDefault();
                  handlePageChange(currentPage - 1);
                }}
                className={currentPage === 1 ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>

            {[...Array(totalPages || 1)].map((_, index) => {
              const page = index + 1;
              return (
                <PaginationItem key={page}>
                  <PaginationLink
                    href="#"
                    onClick={e => {
                      e.preventDefault();
                      handlePageChange(page);
                    }}
                    isActive={page === currentPage}
                  >
                    {page}
                  </PaginationLink>
                </PaginationItem>
              );
            })}

            <PaginationItem>
              <PaginationNext
                href="#"
                onClick={e => {
                  e.preventDefault();
                  handlePageChange(currentPage + 1);
                }}
                className={currentPage === totalPages ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      </div>
    </div>
  );
}
