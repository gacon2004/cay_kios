'use client';

import { useRouter } from 'next/navigation';
import { createContext, useContext, useState, ReactNode } from 'react';

interface Patient {
    national_id: string;
    full_name: string;
    date_of_birth: string;
    gender: string;
    phone: string;
    ward: string;
    district: string;
    province: string;
    ethnicity: string;
    occupation: string;
}

interface Service {
    id: string;
    name: string;
    price: number;
    description: string;
}

interface Room {
    clinic_id: number;
    clinic_name: string;
    clinic_status: string;
    doctor_id: number;
    doctor_name: string;
    phone: string;
}

interface Appointment {
    id: number;
    patient_id: number;
    clinic_id: number;
    service_id: number;
    doctor_id: number;
    schedule_id: number;
    queue_number: number;
    shift_number: number;
    estimated_time: string;
    printed: number;
    status: number;
    booking_channel: string;
    cur_price: number;
    service_name: string;
    service_price: number;
    doctor_name: string;
    clinic_name: string;
    payment_info?: PaymentInfo;
}

interface PaymentInfo {
    patient_name: string;
    patient_national_id: string;
    patient_dob: string;
    patient_gender: string;
    patient_phone: string;
    service_name: string;
    clinic_name: string;
    doctor_name: string;
    shift_number: number;
    queue_number: number;
    price_vnd: number;
    estimated_time: string;
    pay_status: string;
    paid_at: string;
    order_code: string;
    qr_code_url: string;
}

interface AppContextType {
    order_code: string | null;
    setOrderCode: (code: string | null) => void;
    currentStep: number;
    setCurrentStep: (step: number) => void;
    patient: Patient | null;
    setPatient: (patient: Patient | null) => void;
    selectedService: Service | null;
    setSelectedService: (service: Service | null) => void;
    selectedRoom: Room | null;
    setSelectedRoom: (room: Room | null) => void;
    appointment: Appointment | null;
    setAppointment: (appointment: Appointment | null) => void;
    resetApp: () => void;
}

export type { Patient, Service, Room, Appointment, PaymentInfo };

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useAppContext() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
}

export function AppProvider({ children }: { children: ReactNode }) {
    const router = useRouter();
    const [currentStep, setCurrentStep] = useState(1);
    const [order_code, setOrderCode] = useState<string | null>(null);
    const [patient, setPatient] = useState<Patient | null>(null);
    const [selectedService, setSelectedService] = useState<Service | null>(
        null
    );
    const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
    const [appointment, setAppointment] = useState<Appointment | null>(null);

    const resetApp = () => {
        router.push('/');
        setCurrentStep(1);
        setPatient(null);
        setSelectedService(null);
        setSelectedRoom(null);
        setAppointment(null);
        setOrderCode(null);
    };

    return (
        <AppContext.Provider
            value={{
                currentStep,
                setCurrentStep,
                patient,
                setPatient,
                selectedService,
                setSelectedService,
                selectedRoom,
                setSelectedRoom,
                appointment,
                setAppointment,
                order_code,
                setOrderCode,
                resetApp,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}
