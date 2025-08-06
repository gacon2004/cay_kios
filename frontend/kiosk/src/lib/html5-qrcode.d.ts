/* eslint-disable @typescript-eslint/no-misused-new */
/* eslint-disable @typescript-eslint/no-explicit-any */
declare module 'html5-qrcode' {
    // Interface cho kết quả quét QR
    export interface Html5QrcodeResult {
        decodedText: string;
        result: {
            text: string;
            format?: {
                format: number;
                formatName: string;
            };
        };
    }

    // Interface cho cấu hình quét QR
    export interface Html5QrcodeConfig {
        fps: number;
        qrbox?: { width: number; height: number } | number;
        aspectRatio?: number;
        disableFlip?: boolean;
        videoConstraints?: MediaTrackConstraints;
    }

    // Interface cho cấu hình Html5QrcodeScanner
    export interface Html5QrcodeScannerConfig extends Html5QrcodeConfig {
        rememberLastUsedCamera?: boolean;
        supportedScanTypes?: number[];
    }

    // Interface cho thiết bị camera
    export interface CameraDevice {
        id: string;
        label: string;
    }

    // Interface cho instance của Html5Qrcode
    export interface Html5QrcodeInstance {
        start(
            cameraIdOrConfig: string | { facingMode: string },
            configuration: Html5QrcodeConfig,
            qrCodeSuccessCallback: (
                decodedText: string,
                decodedResult: Html5QrcodeResult
            ) => void,
            qrCodeErrorCallback?: (errorMessage: string) => void
        ): Promise<void>;
        stop(): Promise<void>;
        pause(): void;
        resume(): void;
        clear(): void;
        getRunningTrackCapabilities(): MediaTrackCapabilities;
        applyVideoConstraints(
            constraints: MediaTrackConstraints
        ): Promise<void>;
        getState(): number;
        logger: any;
        elementId: string;
        verbose: boolean;
        qrcode: any;
    }

    // Interface cho Html5QrcodeScanner
    export interface Html5QrcodeScanner {
        new (
            elementId: string,
            config: Html5QrcodeScannerConfig,
            verbose?: boolean
        ): Html5QrcodeScanner;
        render(
            qrCodeSuccessCallback: (
                decodedText: string,
                decodedResult: Html5QrcodeResult
            ) => void,
            qrCodeErrorCallback?: (errorMessage: string) => void
        ): void;
        clear(): Promise<void>;
    }

    // Interface cho constructor và các phương thức static
    export interface Html5Qrcode {
        new (elementId: string, verbose?: boolean): Html5QrcodeInstance;
        getCameras(): Promise<CameraDevice[]>;
    }

    export const Html5Qrcode: Html5Qrcode;
    export const Html5QrcodeScanner: Html5QrcodeScanner;

    // Khai báo các hằng số hoặc enum
    export const Html5QrcodeScannerStates: {
        SCANNING: number;
        PAUSED: number;
        STOPPED: number;
    };

    export enum Html5QrcodeScanType {
        SCAN_TYPE_CAMERA = 0,
        SCAN_TYPE_FILE = 1,
    }
}
