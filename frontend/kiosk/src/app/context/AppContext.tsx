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
    clinic_name: string;
    doctor_name: string;
    queue_number: number;
    qr_code: string;
    appointment_time: string;
}

interface AppContextType {
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

export type { Patient, Service, Room, Appointment };

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
                resetApp,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}
