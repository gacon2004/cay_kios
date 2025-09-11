import React, { useState, useEffect } from 'react';
import {
    X,
    Calendar as CalendarIcon,
    Clock,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';
import {
    format,
    addMonths,
    subMonths,
    getDaysInMonth,
    startOfMonth,
    getDay,
} from 'date-fns';
import { vi } from 'date-fns/locale';
import api from '@/app/axios/api';
import type { Service, Room } from '@/app/context/AppContext';

interface PickCalendarProps {
    room: Room;
    service: Service;
    onScheduleSelect: (work_date: string, schedule_id: number) => void;
    onClose: () => void;
}

interface Shift {
    schedule_id: number;
    start_time: string;
    end_time: string;
    remaining: number;
    note: string;
}

interface CalendarResponse {
    work_date: string;
    shifts_count: number;
    total_capacity: number;
    total_booked: number;
    total_remaining: number;
}

const PickCalendar: React.FC<PickCalendarProps> = ({
    room,
    service,
    onScheduleSelect,
    onClose,
}) => {
    const [workDates, setWorkDates] = useState<string[]>([]);
    const [selectedDate, setSelectedDate] = useState<string | null>(null);
    const [shifts, setShifts] = useState<Shift[]>([]);
    const [loadingCalendar, setLoadingCalendar] = useState(true);
    const [loadingShifts, setLoadingShifts] = useState(false);
    const [currentMonth, setCurrentMonth] = useState(new Date(2025, 8, 1));

    useEffect(() => {
        const fetchCalendar = async () => {
            setLoadingCalendar(true);
            try {
                const monthStr = format(currentMonth, 'yyyy-MM');
                const response = await api.get(
                    `/schedule-doctors/calendar?doctor_id=${room.doctor_id}&clinic_id=${room.clinic_id}&month=${monthStr}`
                );
                const dates = response.data.map(
                    (item: CalendarResponse) => item.work_date
                );
                setWorkDates(dates || []);
            } catch (error) {
                console.error('Failed to fetch calendar:', error);
            } finally {
                setLoadingCalendar(false);
            }
        };
        fetchCalendar();
    }, [room.doctor_id, room.clinic_id, currentMonth]);

    useEffect(() => {
        if (selectedDate) {
            const fetchShifts = async () => {
                setLoadingShifts(true);
                try {
                    const response = await api.get(
                        `/schedule-doctors/day-shifts?doctor_id=${room.doctor_id}&clinic_id=${room.clinic_id}&work_date=${selectedDate}`
                    );
                    setShifts(response.data || []);
                } catch (error) {
                    console.error('Failed to fetch shifts:', error);
                } finally {
                    setLoadingShifts(false);
                }
            };
            fetchShifts();
        }
    }, [selectedDate, room.doctor_id, room.clinic_id]);

    const generateCalendarDays = () => {
        const daysInMonth = getDaysInMonth(currentMonth);
        const firstDay = getDay(startOfMonth(currentMonth));
        const adjustedFirstDay = (firstDay + 6) % 7;
        const days = [];
        for (let i = 0; i < adjustedFirstDay; i++) {
            days.push(null);
        }
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = format(
                new Date(
                    currentMonth.getFullYear(),
                    currentMonth.getMonth(),
                    day
                ),
                'yyyy-MM-dd'
            );
            days.push(dateStr);
        }
        return days;
    };

    const calendarDays = generateCalendarDays();

    const handleDateSelect = (date: string | null) => {
        if (date && workDates.includes(date)) {
            setSelectedDate(date);
        } else {
            setSelectedDate(null);
            setShifts([]);
        }
    };

    const handleShiftSelect = (shift: Shift) => {
        if (
            shift.remaining > 0 &&
            selectedDate &&
            window.confirm(
                `Xác nhận chọn ca ${shift.note} vào ${new Date(
                    selectedDate
                ).toLocaleDateString('vi-VN')}?`
            )
        ) {
            onScheduleSelect(selectedDate, shift.schedule_id);
        }
    };

    const handlePrevMonth = () => {
        setCurrentMonth(subMonths(currentMonth, 1));
        setSelectedDate(null);
        setShifts([]);
    };

    const handleNextMonth = () => {
        setCurrentMonth(addMonths(currentMonth, 1));
        setSelectedDate(null);
        setShifts([]);
    };

    return (
        <div className="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-2xl p-7 w-full max-w-4xl mx-4 h-[65vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h3 className="text-2xl font-bold text-gray-900">
                            Chọn Ngày và Ca Khám
                        </h3>
                        <p className="text-gray-600 capitalize">
                            Dịch vụ: {service.name} - Phòng: {room.clinic_name}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                    <div className="w-full md:w-1/2">
                        <div className="flex justify-between items-center mb-4">
                            <button
                                onClick={handlePrevMonth}
                                className="text-gray-600 hover:text-gray-900"
                            >
                                <ChevronLeft size={24} />
                            </button>
                            <h4 className="text-lg font-semibold">
                                {format(currentMonth, 'MMMM yyyy', {
                                    locale: vi,
                                })}
                            </h4>
                            <button
                                onClick={handleNextMonth}
                                className="text-gray-600 hover:text-gray-900"
                            >
                                <ChevronRight size={24} />
                            </button>
                        </div>
                        {loadingCalendar ? (
                            <div className="text-center py-8">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                                <p className="text-gray-600 mt-4">
                                    Đang tải lịch...
                                </p>
                            </div>
                        ) : (
                            <div
                                className="grid grid-cols-7 gap-2 text-center"
                                style={{
                                    minHeight: '300px',
                                    gridTemplateRows:
                                        'repeat(6, minmax(0, 1fr))',
                                }}
                            >
                                {['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'].map(
                                    weekDay => (
                                        <div
                                            key={weekDay}
                                            className="font-semibold text-gray-600"
                                        >
                                            {weekDay}
                                        </div>
                                    )
                                )}
                                {calendarDays.map((date, index) => (
                                    <div
                                        key={index}
                                        className={`w-10 h-10 flex items-center justify-center rounded-full cursor-pointer ${
                                            date
                                                ? workDates.includes(date)
                                                    ? 'bg-[#006e66] text-white hover:bg-[#005a55]'
                                                    : 'text-gray-600'
                                                : 'text-gray-300 cursor-default'
                                        } ${
                                            selectedDate === date
                                                ? 'ring-2 ring-blue-500'
                                                : ''
                                        }`}
                                        onClick={() => handleDateSelect(date)}
                                    >
                                        {date ? new Date(date).getDate() : ''}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="w-full md:w-1/2">
                        <div className="text-center mb-4">
                            <h4 className="text-lg font-semibold">
                                Ca khám cho ngày{' '}
                                {selectedDate
                                    ? new Date(selectedDate).toLocaleDateString(
                                          'vi-VN'
                                      )
                                    : 'Chọn ngày để xem'}
                            </h4>
                        </div>
                        {loadingShifts ? (
                            <div className="text-center py-8">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                                <p className="text-gray-600 mt-4">
                                    Đang tải ca...
                                </p>
                            </div>
                        ) : selectedDate ? (
                            shifts.length > 0 ? (
                                <div className="space-y-4">
                                    {shifts.map(shift => (
                                        <div
                                            key={shift.schedule_id}
                                            className={`p-4 rounded-lg border ${
                                                shift.remaining > 0
                                                    ? 'border-green-200 bg-green-50 hover:bg-green-100 cursor-pointer'
                                                    : 'border-gray-200 bg-gray-50 opacity-60 cursor-not-allowed'
                                            }`}
                                            onClick={() =>
                                                handleShiftSelect(shift)
                                            }
                                        >
                                            <div className="flex justify-between items-center mb-2">
                                                <span className="font-semibold">
                                                    {shift.note}
                                                </span>
                                                <span className="text-sm text-gray-600">
                                                    Chỗ còn lại:{' '}
                                                    {shift.remaining}
                                                </span>
                                            </div>
                                            <div className="flex items-center text-gray-600">
                                                <Clock
                                                    size={16}
                                                    className="mr-2"
                                                />
                                                {shift.start_time} -{' '}
                                                {shift.end_time}
                                            </div>
                                            {shift.remaining === 0 && (
                                                <p className="text-red-500 text-sm mt-2">
                                                    Đã hết chỗ
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-center text-gray-600">
                                    Không có ca khám cho ngày này
                                </p>
                            )
                        ) : (
                            <p className="text-center text-gray-600">
                                Vui lòng chọn ngày từ lịch
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PickCalendar;
