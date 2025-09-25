'use client';

import React, { useState, useEffect } from 'react';
import { CreditCard, User, Phone, Calendar, Scan } from 'lucide-react';
import { Patient, useAppContext } from '../context/AppContext';
import NumericKeyboard from './NumericKeyboard';
import CCCDScanner from './CCCDScanner';
import { useToast } from './ui/use-toast';
import api from '@/app/axios/api';
import { usePathname } from 'next/navigation';

// Interface cho dữ liệu từ API provinces.open-api.vn
interface Province {
    code: string;
    name: string;
}

interface Ward {
    code: string;
    name: string;
}

interface District {
    code: string;
    name: string;
    wards: Ward[];
}

// Interface cho dân tộc và nghề nghiệp
interface Ethnicity {
    code: string;
    name: string;
}

interface Occupation {
    code: string;
    name: string;
}

// Interface cho patientForm
interface PatientForm {
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

const PatientInfo: React.FC = () => {
    const { setCurrentStep, patient, setPatient } = useAppContext();
    const [cccd, setCccd] = useState<string>('');
    const [showKeyboard, setShowKeyboard] = useState<boolean>(false);
    const [patientForm, setPatientForm] = useState<PatientForm>({
        national_id: '',
        full_name: '',
        date_of_birth: '',
        gender: '',
        phone: '',
        ward: '',
        district: '',
        province: '',
        ethnicity: '',
        occupation: '',
    });

    const [showForm, setShowForm] = useState<boolean>(false);
    const [patientExists, setPatientExists] = useState<boolean>(false);
    const [showPhoneKeyboard, setShowPhoneKeyboard] = useState<boolean>(false);
    const [showScanner, setShowScanner] = useState<boolean>(false);
    const [provinces, setProvinces] = useState<Province[]>([]);
    const [districts, setDistricts] = useState<District[]>([]);
    const [wards, setWards] = useState<Ward[]>([]);
    const [ethnicities, setEthnicities] = useState<Ethnicity[]>([]);
    const [isCustomOccupation, setIsCustomOccupation] =
        useState<boolean>(false);
    const [selectedProvinceCode, setSelectedProvinceCode] =
        useState<string>('');
    const [selectedDistrictCode, setSelectedDistrictCode] =
        useState<string>('');

    const { toast } = useToast();
    const [loading, setLoading] = useState<boolean>(false);
    const pathname = usePathname();

    // Danh sách nghề nghiệp tĩnh
    const occupations: Occupation[] = [
        { code: '1', name: 'Nhân viên văn phòng' },
        { code: '2', name: 'Công nhân' },
        { code: '3', name: 'Học sinh/Sinh viên' },
        { code: '4', name: 'Nghỉ hưu' },
        { code: 'custom', name: 'Tự do' },
    ];

    // Danh sách dân tộc tĩnh
    const staticEthnicities: Ethnicity[] = [
        { code: '1', name: 'Kinh' },
        { code: '2', name: 'Tày' },
        { code: '3', name: 'Thái' },
        { code: '4', name: 'Mường' },
        { code: '5', name: 'Hre' },
        { code: '6', name: 'Bru-Vân Kiều' },
        { code: '7', name: 'Xa Phang' },
    ];

    // Lấy danh sách tỉnh/thành phố từ API công khai
    useEffect(() => {
        const fetchProvinces = async () => {
            try {
                const response = await fetch(
                    'https://provinces.open-api.vn/api/p/'
                );
                if (!response.ok) {
                    throw new Error('Không thể tải danh sách tỉnh/thành phố');
                }
                const data: Province[] = await response.json();
                setProvinces(data);
            } catch (error) {
                toast({
                    title: 'Lỗi hệ thống',
                    description: 'Không thể tải danh sách tỉnh/thành phố.',
                });
            }
        };
        fetchProvinces();
    }, [toast]);

    // Lấy danh sách quận/huyện
    useEffect(() => {
        if (selectedProvinceCode) {
            fetch(
                `https://provinces.open-api.vn/api/p/${selectedProvinceCode}?depth=3`
            )
                .then(res => res.json())
                .then(data => setDistricts(data.districts || []))
                .catch(() => setDistricts([]));
        } else {
            setDistricts([]);
        }
    }, [selectedProvinceCode]);

    // Lấy danh sách phường/xã
    useEffect(() => {
        if (selectedDistrictCode && districts.length > 0) {
            const selectedDistrict = districts.find(
                d => String(d.code) === String(selectedDistrictCode)
            );
            setWards(selectedDistrict?.wards || []);
        } else {
            setWards([]);
        }
    }, [selectedDistrictCode, districts]);

    // Gán danh sách dân tộc tĩnh
    useEffect(() => {
        setEthnicities(staticEthnicities);
    }, []);

    const handleCCCDCheck = async (cccdValue: string) => {
        setLoading(true);
        try {
            setPatientForm({ ...patientForm, national_id: cccdValue });

            // Kiểm tra bảo hiểm y tế
            const insuranceResponse = await api.get<{ has_insurance: boolean }>(
                `/insurances/check/${cccdValue}`
            );

            // Lưu trạng thái bảo hiểm

            const hasInsurance =
                insuranceResponse?.data?.has_insurance || false;
            if (localStorage.getItem('has_insurances')) {
                localStorage.removeItem('has_insurances');
            }
            localStorage.setItem(
                'has_insurances',
                JSON.stringify(hasInsurance)
            );

            if (!hasInsurance) {
                toast({
                    title: '🚧 Không tìm thấy thông tin bảo hiểm!',
                    description: 'Bạn được chuyển sang khám dịch vụ ',
                });
            }

            // Tiếp tục đăng nhập để kiểm tra thông tin bệnh nhân
            await loginPatient(cccdValue);
        } catch (error) {
            toast({
                title: 'Lỗi hệ thống',
                description:
                    'Không thể xử lý thông tin CCCD. Vui lòng thử lại.',
            });
            console.error('Error in handleCCCDCheck:', error);
        } finally {
            setLoading(false);
        }
    };

    const loginPatient = async (nationalId: string) => {
        try {
            // Gửi yêu cầu đăng nhập
            const loginResponse = await api.post<{
                token: { access_token: string; refresh_token: string };
            }>('/auth/patient/login', { national_id: nationalId });

            if (!loginResponse?.data?.token?.access_token) {
                throw new Error('Không thể đăng nhập: Token không hợp lệ');
            }

            const { access_token, refresh_token } = loginResponse.data.token;
            if (localStorage.getItem('access_token')) {
                localStorage.removeItem('access_token');
            }
            if (localStorage.getItem('refresh_token')) {
                localStorage.removeItem('refresh_token');
            }
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Kiểm tra thông tin bệnh nhân
            try {
                const patientResponse = await api.get<Patient>('/patients/me');
                if (patientResponse?.data) {
                    setPatient(patientResponse.data);
                    setPatientExists(true);
                    setShowForm(false); // Không hiển thị form nếu bệnh nhân đã tồn tại
                } else {
                    setShowForm(true); // Hiển thị form nếu không tìm thấy thông tin bệnh nhân
                }
            } catch (error) {
                // Nếu không tìm thấy thông tin bệnh nhân, mở form nhập
                setShowForm(true);
                setPatientExists(false);
                toast({
                    title: '🚧 Không tìm thấy thông tin bệnh nhân',
                    description: 'Vui lòng đăng ký tại đây !',
                });
            }
        } catch (error) {
            toast({
                title: 'Không có thông tin bệnh nhân !',
                description: 'Vui lòng đăng ký thông tin tại đây',
            });
            console.error('Error in loginPatient:', error);
            setShowForm(true); // Hiển thị form nếu có lỗi đăng nhập
        }
    };

    const handleScanSuccess = async (scannedCCCD: string) => {
        setCccd(scannedCCCD);
        setShowScanner(false);
        await handleCCCDCheck(scannedCCCD);
    };

    const handleCCCDSubmit = async () => {
        if (cccd.length !== 12) {
            toast({
                title: 'CCCD không hợp lệ',
                description: 'CCCD phải có đúng 12 số.',
            });
            return;
        }
        await handleCCCDCheck(cccd);
    };

    const handleFormSubmit = async () => {
        const requiredFields = [
            patientForm.national_id,
            patientForm.full_name,
            patientForm.date_of_birth,
            patientForm.gender,
            patientForm.phone,
            patientForm.ward,
            patientForm.district,
            patientForm.province,
            patientForm.ethnicity,
            patientForm.occupation,
        ];

        if (requiredFields.some(field => !field)) {
            toast({
                title: 'Thiếu thông tin',
                description: 'Vui lòng điền đầy đủ tất cả các trường bắt buộc.',
            });
            return;
        }

        try {
            await api.post('/auth/patient/register', patientForm);
            await loginPatient(patientForm.national_id);
            setPatient(patientForm);
            setPatientExists(true);
        } catch (error) {
            toast({
                title: 'Lỗi đăng ký',
                description: 'Không thể đăng ký bệnh nhân. Vui lòng thử lại.',
            });
            console.error('Error in handleFormSubmit:', error);
        }
    };

    const handleNext = () => {
        setCurrentStep(2);
    };

    if (patientExists && patient) {
        return (
            <div className="w-full">
                <div className="bg-white rounded-2xl shadow-lg p-8">
                    <div className="text-center mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">
                            Thông Tin Bệnh Nhân
                        </h2>
                        <p className="text-gray-600 text-xl">
                            Xác nhận thông tin của bạn
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6  mb-8">
                        <div className="space-y-4 text-xl">
                            <div>
                                <label className="block font-normal text-gray-400 mb-1">
                                    Số CCCD
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.national_id}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Họ và tên
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.full_name}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Ngày sinh
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.date_of_birth}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Giới tính
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.gender}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Nghề nghiệp
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.occupation}
                                </p>
                            </div>
                        </div>
                        <div className="space-y-4 text-xl">
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Số điện thoại
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.phone}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Phường/Xã
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.ward}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Quận/Huyện
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.district}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Tỉnh/Thành phố
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.province}
                                </p>
                            </div>
                            <div>
                                <label className="block  font-normal text-gray-400 mb-1">
                                    Dân tộc
                                </label>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {patient.ethnicity}
                                </p>
                            </div>
                        </div>
                    </div>

                    {pathname !== '/checkAppointments' && (
                        <div className="text-center">
                            <button
                                onClick={handleNext}
                                className="bg-background hover:opacity-80 text-white font-semibold py-4 px-12 rounded-xl transition-colors duration-200 text-lg"
                            >
                                Tiếp tục
                            </button>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    if (showForm) {
        return (
            <div className="w-full">
                <div className="bg-white rounded-2xl shadow-lg p-8">
                    <div className="text-center mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">
                            Nhập Thông Tin Bệnh Nhân
                        </h2>
                        <p className="text-gray-600">
                            Vui lòng cung cấp thông tin chi tiết
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Số CCCD *
                                </label>
                                <input
                                    type="text"
                                    value={patientForm.national_id}
                                    readOnly
                                    className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-100 text-lg"
                                    placeholder="Số CCCD"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Họ và tên *
                                </label>
                                <input
                                    type="text"
                                    value={patientForm.full_name}
                                    onChange={(
                                        e: React.ChangeEvent<HTMLInputElement>
                                    ) =>
                                        setPatientForm({
                                            ...patientForm,
                                            full_name: e.target.value,
                                        })
                                    }
                                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                    placeholder="Nhập họ và tên"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Ngày sinh *
                                </label>
                                <input
                                    type="date"
                                    value={patientForm.date_of_birth}
                                    onChange={(
                                        e: React.ChangeEvent<HTMLInputElement>
                                    ) =>
                                        setPatientForm({
                                            ...patientForm,
                                            date_of_birth: e.target.value,
                                        })
                                    }
                                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Giới tính *
                                </label>
                                <select
                                    value={patientForm.gender}
                                    onChange={(
                                        e: React.ChangeEvent<HTMLSelectElement>
                                    ) =>
                                        setPatientForm({
                                            ...patientForm,
                                            gender: e.target.value,
                                        })
                                    }
                                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                >
                                    <option value="">Chọn giới tính</option>
                                    <option value="Nam">Nam</option>
                                    <option value="Nữ">Nữ</option>
                                    <option value="Khác">Khác</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Số điện thoại *
                                </label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={patientForm.phone}
                                        readOnly
                                        onClick={() =>
                                            setShowPhoneKeyboard(true)
                                        }
                                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg cursor-pointer"
                                        placeholder="Nhấn để nhập số điện thoại"
                                    />
                                    <Phone
                                        className="absolute right-3 top-3 text-gray-400"
                                        size={20}
                                    />
                                </div>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Tỉnh/Thành phố *
                                </label>
                                <select
                                    value={patientForm.province}
                                    onChange={e => {
                                        const code =
                                            e.target.selectedOptions[0].getAttribute(
                                                'data-code'
                                            ) || '';
                                        const name = e.target.value;
                                        setSelectedProvinceCode(code);
                                        setPatientForm({
                                            ...patientForm,
                                            province: name,
                                            district: '',
                                            ward: '',
                                        });
                                    }}
                                    className="w-full px-4 py-[13px] border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                >
                                    <option value="">
                                        Chọn tỉnh/thành phố
                                    </option>
                                    {provinces.map(province => (
                                        <option
                                            key={province.code}
                                            value={province.name}
                                            data-code={province.code}
                                        >
                                            {province.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Quận/Huyện *
                                </label>
                                <select
                                    value={patientForm.district}
                                    onChange={e => {
                                        const code =
                                            e.target.selectedOptions[0].getAttribute(
                                                'data-code'
                                            ) || '';
                                        const name = e.target.value;
                                        setSelectedDistrictCode(code);
                                        setPatientForm({
                                            ...patientForm,
                                            district: name,
                                            ward: '',
                                        });
                                    }}
                                    className="w-full px-4 py-[13px] border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                >
                                    <option value="">Chọn quận/huyện</option>
                                    {districts.map(district => (
                                        <option
                                            key={district.code}
                                            value={district.name}
                                            data-code={district.code}
                                        >
                                            {district.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Phường/Xã *
                                </label>
                                <select
                                    value={patientForm.ward}
                                    onChange={(
                                        e: React.ChangeEvent<HTMLSelectElement>
                                    ) =>
                                        setPatientForm({
                                            ...patientForm,
                                            ward: e.target.value,
                                        })
                                    }
                                    className="w-full px-4 py-[13px] border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                    disabled={!patientForm.district}
                                >
                                    <option value="">Chọn phường/xã</option>
                                    {wards.map(ward => (
                                        <option
                                            key={ward.code}
                                            value={ward.name}
                                        >
                                            {ward.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Dân tộc *
                                </label>
                                <select
                                    value={patientForm.ethnicity}
                                    onChange={(
                                        e: React.ChangeEvent<HTMLSelectElement>
                                    ) =>
                                        setPatientForm({
                                            ...patientForm,
                                            ethnicity: e.target.value,
                                        })
                                    }
                                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                >
                                    <option value="">Chọn dân tộc</option>
                                    {ethnicities.map(ethnicity => (
                                        <option
                                            key={ethnicity.code}
                                            value={ethnicity.name}
                                        >
                                            {ethnicity.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nghề nghiệp *
                                </label>
                                {isCustomOccupation ? (
                                    <input
                                        type="text"
                                        value={patientForm.occupation}
                                        onChange={(
                                            e: React.ChangeEvent<HTMLInputElement>
                                        ) =>
                                            setPatientForm({
                                                ...patientForm,
                                                occupation: e.target.value,
                                            })
                                        }
                                        className="w-full px-4 py-[13px] border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                        placeholder="Nhập nghề nghiệp"
                                    />
                                ) : (
                                    <select
                                        value={patientForm.occupation}
                                        onChange={(
                                            e: React.ChangeEvent<HTMLSelectElement>
                                        ) => {
                                            if (e.target.value === 'custom') {
                                                setIsCustomOccupation(true);
                                                setPatientForm({
                                                    ...patientForm,
                                                    occupation: '',
                                                });
                                            } else {
                                                setPatientForm({
                                                    ...patientForm,
                                                    occupation: e.target.value,
                                                });
                                            }
                                        }}
                                        className="w-full px-4 py-[13px] border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                                    >
                                        <option value="">
                                            Chọn nghề nghiệp
                                        </option>
                                        {occupations.map(occupation => (
                                            <option
                                                key={occupation.code}
                                                value={occupation.name}
                                            >
                                                {occupation.name}
                                            </option>
                                        ))}
                                    </select>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="text-center">
                        <button
                            onClick={handleFormSubmit}
                            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-4 px-12 rounded-xl transition-colors duration-200 text-lg"
                        >
                            Xác nhận thông tin
                        </button>
                    </div>
                </div>

                {showPhoneKeyboard && (
                    <NumericKeyboard
                        value={patientForm.phone}
                        onChange={(value: string) =>
                            setPatientForm({ ...patientForm, phone: value })
                        }
                        onClose={() => setShowPhoneKeyboard(false)}
                        maxLength={10}
                    />
                )}
            </div>
        );
    }

    return (
        <div className="w-full">
            {loading ? (
                <div className="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50">
                    <div className="text-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                        <p className="text-gray-600 mt-2">Đang kiểm tra...</p>
                    </div>
                </div>
            ) : (
                ''
            )}
            <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Nhập Số CCCD
                    </h2>
                    <p className="text-gray-600">
                        Vui lòng nhập số căn cước công dân (12 số)
                    </p>
                </div>

                <div className="max-w-md mx-auto mb-8">
                    <div
                        className="relative cursor-pointer"
                        onClick={() => setShowKeyboard(true)}
                    >
                        <input
                            type="text"
                            value={cccd}
                            readOnly
                            className="w-full px-6 py-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-2xl font-semibold text-center cursor-pointer"
                            placeholder="Nhấn để nhập CCCD"
                        />
                        <CreditCard
                            className="absolute right-4 top-4 text-gray-400"
                            size={24}
                        />
                    </div>

                    <div className="mt-6">
                        <button
                            onClick={() => setShowScanner(true)}
                            className="flex items-center justify-center text-lg w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-xl transition-colors duration-200 cursor-pointer"
                        >
                            <Scan className="mr-3" size={24} />
                            Quét thẻ CCCD
                        </button>
                    </div>
                </div>

                <div className="text-center">
                    <button
                        onClick={handleCCCDSubmit}
                        disabled={cccd.length !== 12}
                        className="bg-background hover:opacity-85 disabled:bg-gray-300 text-white font-semibold py-4 px-12 rounded-xl transition-colors duration-200 text-lg cursor-pointer"
                    >
                        Xác nhận
                    </button>
                </div>
            </div>

            {showKeyboard && (
                <NumericKeyboard
                    value={cccd}
                    onChange={setCccd}
                    onClose={() => setShowKeyboard(false)}
                    maxLength={12}
                />
            )}

            {showScanner && (
                <CCCDScanner
                    onScanSuccess={handleScanSuccess}
                    onClose={() => setShowScanner(false)}
                />
            )}
        </div>
    );
};

export default PatientInfo;
