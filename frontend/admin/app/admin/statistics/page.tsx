'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import axiosInstance from '@/lib/axiosInstance';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { TrendingUp, Users, Calendar, DollarSign } from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export default function StatisticsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7days');

  useEffect(() => {
    fetchStatistics();
  }, [timeRange]);

  const fetchStatistics = async () => {
    try {
      // Simulate API calls
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Mock data for demonstration
  const appointmentTrends = [
    { date: '2024-01-14', appointments: 12, revenue: 2400000 },
    { date: '2024-01-15', appointments: 19, revenue: 3800000 },
    { date: '2024-01-16', appointments: 15, revenue: 3000000 },
    { date: '2024-01-17', appointments: 22, revenue: 4400000 },
    { date: '2024-01-18', appointments: 18, revenue: 3600000 },
    { date: '2024-01-19', appointments: 25, revenue: 5000000 },
    { date: '2024-01-20', appointments: 20, revenue: 4000000 },
  ];

  const serviceDistribution = [
    { name: 'General Checkup', value: 35, color: '#3B82F6' },
    { name: 'Blood Test', value: 28, color: '#10B981' },
    { name: 'X-Ray', value: 22, color: '#F59E0B' },
    { name: 'Consultation', value: 18, color: '#EF4444' },
    { name: 'Lab Work', value: 12, color: '#8B5CF6' },
  ];

  const doctorPerformance = [
    { name: 'Dr. Sarah Johnson', appointments: 45, rating: 4.8 },
    { name: 'Dr. Michael Chen', appointments: 38, rating: 4.7 },
    { name: 'Dr. Emily Wang', appointments: 32, rating: 4.9 },
    { name: 'Dr. James Brown', appointments: 28, rating: 4.6 },
  ];

  const patientFlow = [
    { hour: '08:00', patients: 5 },
    { hour: '09:00', patients: 12 },
    { hour: '10:00', patients: 18 },
    { hour: '11:00', patients: 15 },
    { hour: '12:00', patients: 8 },
    { hour: '13:00', patients: 6 },
    { hour: '14:00', patients: 14 },
    { hour: '15:00', patients: 20 },
    { hour: '16:00', patients: 16 },
    { hour: '17:00', patients: 10 },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Statistics & Analytics"
        description="Comprehensive insights into kiosk performance and usage patterns"
      >
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7days">Last 7 days</SelectItem>
            <SelectItem value="30days">Last 30 days</SelectItem>
            <SelectItem value="90days">Last 3 months</SelectItem>
            <SelectItem value="1year">Last year</SelectItem>
          </SelectContent>
        </Select>
      </PageHeader>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">₫26.8M</p>
                <p className="text-sm text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12.5% vs last week
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Patients</p>
                <p className="text-2xl font-bold text-blue-600">1,247</p>
                <p className="text-sm text-blue-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8.2% vs last week
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Appointments</p>
                <p className="text-2xl font-bold text-purple-600">149</p>
                <p className="text-sm text-purple-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +15.3% vs last week
                </p>
              </div>
              <Calendar className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg. Wait Time</p>
                <p className="text-2xl font-bold text-orange-600">12 min</p>
                <p className="text-sm text-red-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1 rotate-180" />
                  -3.1% vs last week
                </p>
              </div>
              <Calendar className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appointment Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Appointment & Revenue Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={appointmentTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value, name) => [
                    name === 'revenue' ? `₫${value.toLocaleString()}` : value,
                    name === 'appointments' ? 'Appointments' : 'Revenue'
                  ]}
                />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="appointments"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.1}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="revenue"
                  stroke="#10B981"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Service Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Service Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={serviceDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {serviceDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Doctor Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Doctor Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={doctorPerformance} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="appointments" fill="#3B82F6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Patient Flow */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Patient Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={patientFlow}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="patients" 
                  stroke="#10B981" 
                  strokeWidth={3}
                  dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Peak Hours</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Morning Peak</span>
                <span className="font-medium">9:00 - 11:00 AM</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Afternoon Peak</span>
                <span className="font-medium">2:00 - 4:00 PM</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Busiest Day</span>
                <span className="font-medium">Friday</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Patient Demographics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Age 18-30</span>
                <span className="font-medium">28%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Age 31-50</span>
                <span className="font-medium">45%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Age 51+</span>
                <span className="font-medium">27%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Uptime</span>
                <span className="font-medium text-green-600">99.8%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Response Time</span>
                <span className="font-medium">1.2s</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="font-medium text-green-600">0.1%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}