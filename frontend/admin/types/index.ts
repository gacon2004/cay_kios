export interface User {
  id: string;
  email: string;
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
  id: string;
  name: string;
  email?: string;
  phone: string;
  cccd: string;
  dateOfBirth: string;
  gender: "male" | "female" | "other";
  address: string;
  createdAt: string;
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
  id: string;
  name: string;
  type: string;
  status: "available" | "occupied" | "maintenance";
  equipment: string[];
  createdAt: string;
}

export interface Appointment {
  id: string;
  patientId: string;
  doctorId: string;
  serviceId: string;
  roomId: string;
  patient: Patient;
  doctor: Doctor;
  service: Service;
  room: Room;
  scheduledAt: string;
  status: "scheduled" | "in-progress" | "completed" | "cancelled";
  notes?: string;
  createdAt: string;
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
