/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { X, CheckCircle, AlertCircle } from 'lucide-react';
import { BrowserQRCodeReader } from '@zxing/browser';

interface CCCDScannerProps {
    onScanSuccess: (cccd: string) => void;
    onClose: () => void;
}

const CCCDScanner = ({ onScanSuccess, onClose }: CCCDScannerProps) => {
    const [scanResult, setScanResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isScanning, setIsScanning] = useState(false);

    const videoRef = useRef<HTMLVideoElement>(null);
    const codeReaderRef = useRef<BrowserQRCodeReader | null>(null);
    const controlsRef = useRef<{ stop: () => void } | null>(null);
    const isMountedRef = useRef(true);

    // useEffect unmount
    useEffect(() => {
        isMountedRef.current = true;
        return () => {
            isMountedRef.current = false;
            cleanup();
        };
    }, []);

    const cleanup = useCallback(async () => {
        if (controlsRef.current) {
            try {
                console.log('Stopping ZXing scanner...');
                controlsRef.current.stop();
                console.log('ZXing scanner stopped.');
            } catch (err: any) {
                console.log('ZXing cleanup error:', err?.message || err);
            }
            controlsRef.current = null;
        }

        // Stop media tracks manually if still active
        const video = videoRef.current;
        if (video?.srcObject) {
            const mediaStream = video.srcObject as MediaStream;
            mediaStream.getTracks().forEach(track => {
                track.stop();
            });
            video.srcObject = null;
            console.log('All media tracks stopped.');
        }

        codeReaderRef.current = null;

        if (isMountedRef.current) {
            setIsScanning(false);
        }
    }, []);

    const startScanning = useCallback(async () => {
        if (!videoRef.current) {
            console.log('Video element not ready');
            setError('Không tìm thấy phần tử video');
            return;
        }

        if (!isMountedRef.current) {
            console.log('Component unmounted, aborting start');
            return;
        }

        // Cleanup any existing scanner
        await cleanup();

        try {
            setIsScanning(true);
            setError(null);
            setScanResult(null);

            // Initialize ZXing QR code reader
            codeReaderRef.current = new BrowserQRCodeReader();

            // Start scanning with default camera
            controlsRef.current =
                await codeReaderRef.current.decodeFromVideoDevice(
                    undefined, // Use default camera
                    videoRef.current,
                    async (result, error) => {
                        if (!isMountedRef.current) return;

                        if (result) {
                            const decodedText = result.getText();
                            console.log(`[+] Phát hiện: ${decodedText}`);
                            const cccdNumber = decodedText
                                .replace(/\D/g, '')
                                .slice(0, 12);

                            if (cccdNumber.length === 12) {
                                setScanResult(cccdNumber);
                                setError(null);

                                // 🛑 Cleanup camera ngay sau khi quét thành công
                                await cleanup();

                                setTimeout(() => {
                                    if (isMountedRef.current) {
                                        onScanSuccess(cccdNumber);
                                    }
                                }, 2000);
                            } else {
                                setScanResult(decodedText);
                                setError(
                                    'Mã QR không đúng định dạng CCCD (12 số)'
                                );
                            }
                        } else if (error) {
                            const errorMessage = error.message || String(error);
                            if (!errorMessage.includes('No QR code found')) {
                                console.log(`Scan error: ${errorMessage}`);
                                setError(
                                    'Không thể quét mã QR. Vui lòng chụp ảnh lại và phóng to QR ra gấp 2 lần.'
                                );
                            }
                        }
                    }
                );

            console.log('Scanner started successfully');
        } catch (err: any) {
            console.error('Error starting scanner:', err);
            if (isMountedRef.current) {
                setError(`Lỗi khởi động camera: ${err.message || err}`);
                setIsScanning(false);
                controlsRef.current = null;
                codeReaderRef.current = null;
            }
            // Retry after 3 seconds
            setTimeout(() => {
                if (isMountedRef.current && !controlsRef.current) {
                    console.log('Retrying scanner start...');
                    startScanning();
                }
            }, 3000);
        }
    }, [onScanSuccess]);

    // Start scanner on mount
    useEffect(() => {
        startScanning();
    }, [startScanning]);

    const handleClose = async () => {
        await cleanup();
        if (isMountedRef.current) {
            onClose();
        }
    };

    const confirmResult = () => {
        if (scanResult) {
            onScanSuccess(scanResult);
        }
    };

    return (
        <div className="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="text-xl font-bold text-gray-900">
                        Quét Mã QR Thẻ CCCD
                    </h3>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <X size={24} />
                    </button>
                </div>
                <div className="p-4">
                    {/* Camera Scanner */}
                    <div className="relative mb-4">
                        <video
                            ref={videoRef}
                            className="w-full border-4 border-blue-500 rounded-lg"
                            style={{
                                minHeight: '400px',
                                objectFit: 'cover',
                                filter: 'contrast(1.5) brightness(1.1)',
                            }}
                        />
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 border-2 border-dashed border-red-500 w-[400px] h-[400px] opacity-50" />
                    </div>
                    {/* Status */}
                    {isScanning && !scanResult && !error && (
                        <div className="text-center p-4 bg-blue-50 rounded-lg mb-4">
                            <p className="text-blue-800 font-medium">
                                Đang quét mã QR... Vui lòng đưa mã QR vào khung
                                camera
                            </p>
                        </div>
                    )}
                    {/* Result */}
                    {scanResult && (
                        <div className="text-center p-4 bg-green-50 rounded-lg mb-4">
                            <div className="flex items-center justify-center mb-2">
                                <CheckCircle
                                    className="text-green-500 mr-2"
                                    size={24}
                                />
                                <h4 className="text-lg font-semibold text-green-800">
                                    Quét thành công!
                                </h4>
                            </div>
                            <p className="text-green-700 mb-2">Kết quả quét:</p>
                            <div className="bg-white rounded p-3 mb-4">
                                <p className="text-xl font-mono font-bold text-gray-900">
                                    {scanResult}
                                </p>
                            </div>
                            <button
                                onClick={confirmResult}
                                className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                            >
                                Xác nhận
                            </button>
                        </div>
                    )}
                    {/* Error */}
                    {error && (
                        <div className="text-center p-4 bg-red-50 rounded-lg mb-4">
                            <div className="flex items-center justify-center mb-2">
                                <AlertCircle
                                    className="text-red-500 mr-2"
                                    size={24}
                                />
                                <h4 className="text-lg font-semibold text-red-800">
                                    Có lỗi xảy ra
                                </h4>
                            </div>
                            <p className="text-red-600 mb-4">{error}</p>
                            <div className="flex justify-center gap-4">
                                <button
                                    onClick={startScanning}
                                    className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                                >
                                    Thử lại
                                </button>
                                <button
                                    onClick={handleClose}
                                    className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                                >
                                    Đóng
                                </button>
                            </div>
                        </div>
                    )}
                    {/* Instructions */}
                    {!scanResult && !error && (
                        <div className="text-center text-gray-600">
                            <p className="mb-2">
                                • Đặt mã QR trên thẻ CCCD vào khung viền đỏ
                            </p>
                            <p className="mb-2">
                                • Đưa thẻ gần camera (khoảng 10-15cm)
                            </p>
                            <p className="mb-2">
                                • Đảm bảo ánh sáng đủ, không quá tối hoặc chói
                            </p>
                            <p>• Giữ thẻ ổn định cho đến khi quét thành công</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CCCDScanner;
