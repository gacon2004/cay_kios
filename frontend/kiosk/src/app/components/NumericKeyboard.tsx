import React, { useEffect, useRef } from 'react';
import { Delete, X } from 'lucide-react';

interface NumericKeyboardProps {
    value: string;
    onChange: (value: string) => void;
    onClose: () => void;
    maxLength?: number;
}

const NumericKeyboard: React.FC<NumericKeyboardProps> = ({
    value,
    onChange,
    onClose,
    maxLength = 12,
}) => {
    const inputRef = useRef<HTMLInputElement>(null);

    const handleNumberClick = (num: string) => {
        if (value.length >= maxLength) return;
        onChange(value + num); // Thêm số trực tiếp, không kiểm tra số 0 ở đầu
    };

    const handleBackspace = () => {
        const newValue = value.slice(0, -1);
        onChange(newValue); // Trả về '0' nếu chuỗi rỗng
    };

    const handleClear = () => {
        onChange(''); // Đặt lại về '0'
    };

    const handleKeyDown = (event: KeyboardEvent) => {
        const { key } = event;

        // Cho phép các phím số 0-9
        if (/^[0-9]$/.test(key) && value.length < maxLength) {
            event.preventDefault();
            onChange(value + key); // Thêm số trực tiếp, không kiểm tra số 0 ở đầu
        }
        // Xử lý phím Backspace
        else if (key === 'Backspace') {
            event.preventDefault();
            handleBackspace();
        }
        // Xử lý phím C để xóa
        else if (key.toLowerCase() === 'c') {
            event.preventDefault();
            handleClear();
        }
        // Xử lý phím Enter hoặc Escape để đóng
        else if (key === 'Enter' || key === 'Escape') {
            event.preventDefault();
            onClose();
        }
    };

    useEffect(() => {
        // Thêm sự kiện keydown khi component được mount
        window.addEventListener('keydown', handleKeyDown);
        // Focus vào input khi component được mount
        inputRef.current?.focus();
        // Dọn dẹp sự kiện khi component unmount
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [value]);

    const numbers = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['C', '0', '⌫'],
    ];

    return (
        <div className="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md mx-4">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900">
                        Nhập số
                    </h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                        type="button"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="mb-6">
                    <input
                        ref={inputRef}
                        type="text"
                        value={value}
                        onChange={e => {
                            const newValue = e.target.value.replace(
                                /[^0-9]/g,
                                ''
                            );
                            onChange(newValue || '');
                        }}
                        className="w-full bg-gray-100 rounded-xl p-4 text-center text-2xl font-mono text-gray-900 focus:outline-none"
                        maxLength={maxLength}
                        readOnly // Ngăn nhập trực tiếp vào input để kiểm soát tốt hơn
                    />
                </div>

                <div className="grid grid-cols-3 gap-3">
                    {numbers.map((row, rowIndex) =>
                        row.map((key, keyIndex) => (
                            <button
                                key={`${rowIndex}-${keyIndex}`}
                                type="button"
                                onClick={() => {
                                    if (key === 'C') {
                                        handleClear();
                                    } else if (key === '⌫') {
                                        handleBackspace();
                                    } else {
                                        handleNumberClick(key);
                                    }
                                }}
                                className={`h-16 rounded-xl font-semibold text-xl transition-all duration-200 ${
                                    key === 'C'
                                        ? 'bg-red-500 hover:bg-red-600 text-white'
                                        : key === '⌫'
                                        ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                                        : 'bg-background hover:bg-blue-600 text-white'
                                } hover:transform hover:scale-105 active:scale-95 focus:outline-none`}
                            >
                                {key === '⌫' ? (
                                    <Delete size={20} className="mx-auto" />
                                ) : (
                                    key
                                )}
                            </button>
                        ))
                    )}
                </div>

                <div className="mt-6 text-center">
                    <button
                        onClick={onClose}
                        type="button"
                        className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-8 rounded-xl transition-colors duration-200 focus:outline-none"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NumericKeyboard;
