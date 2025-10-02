export interface User {
  id: string;
  name: string;
  role: string;
}

export interface Doctor {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  specialty: string | null;
  status?: "active" | "inactive";
  created_at: string;
}

export interface Patient {
  id: number;
  national_id: string;
  full_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  ward: string;
  district: string;
  province: string;
  occupation: string;
  ethnicity: string;
  created_at: string;
}

export interface Service {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number;
  status: "active" | "inactive";
  createdAt: string;
}

export interface Room {
  id: number;
  name: string;
  service_id: number;
  location: string;
  status: "Còn trống" | "Đã đầy" | "Bảo trì";
}

export interface ClinicDetails {
  clinic_id: Room["id"];
  clinic_name: string;
  clinic_status: "active" | "full" | "fixed";
  doctor_id: Doctor["id"] | null;
  doctor_name: Doctor["full_name"] | null;
  specialty: string;
  phone: string | null;
  schedule_id: string | null;
  start_time: string | null;
  end_time: string | null;
  max_patients: string | null;
  booked_patients: number | null;
  remaining: string | null;
}

export interface Appointment {
  appointment_id: number;
  clinic_name: string;
  doctor_name: string;
  estimated_time: Date;
  order_code: string;
  paid_at: Date | null;
  patient_dob: string;
  patient_gender: "Nam" | "Nữ" | "Khác";
  patient_name: string;
  patient_national_id: string;
  patient_phone: string;
  pay_status: "AWAITING" | "PAID" | "CANCELLED";
  price_vnd: number;
  queue_number: number;
  service_name: string;
  shift_number: number;
}

export interface Statistics {
  totalPatientsToday: number;
  totalAppointments: number;
  totalDoctors: number;
  topServices: Array<{
    name: string;
    count: number;
  }>;
  appointmentsByStatus: Array<{
    status: string;
    count: number;
  }>;
  revenueToday: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
