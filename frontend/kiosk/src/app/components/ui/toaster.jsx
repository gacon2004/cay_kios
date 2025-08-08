'use client';

import {
    Toast,
    ToastClose,
    ToastDescription,
    ToastProvider,
    ToastTitle,
    ToastViewport,
} from './toast';
import { useToast } from './use-toast';
import React from 'react';

export function Toaster() {
    const { toasts } = useToast();

    return (
        <ToastProvider>
            {toasts.map(
                ({ id, title, description, action, dismiss, ...props }) => {
                    return (
                        <Toast
                            key={id}
                            {...props}
                            className="relative flex w-full items-center justify-between space-x-4 rounded-md border p-6 pr-8 shadow-lg transition-all duration-300 ease-in-out hover:shadow-xl hover:-translate-x-1 bg-white"
                        >
                            <div className="grid gap-1">
                                {title && (
                                    <ToastTitle className="text-lg font-semibold text-gray-900">
                                        {title}
                                    </ToastTitle>
                                )}
                                {description && (
                                    <ToastDescription className="mt-1 text-gray-600">
                                        {description}
                                    </ToastDescription>
                                )}
                            </div>
                            {action}
                            <ToastClose className="text-gray-400 hover:text-gray-600" />
                        </Toast>
                    );
                }
            )}
            <ToastViewport className="fixed bottom-0 right-0 p-6 flex flex-col gap-4 w-[390px] max-w-[100vw]" />
        </ToastProvider>
    );
}
