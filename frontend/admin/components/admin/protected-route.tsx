'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, initializeAuth } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    const publicPaths = ['/admin/login', '/admin/register'];
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';

    if (!isLoading && !isAuthenticated && !publicPaths.includes(currentPath)) {
      console.log('Redirecting to /admin/login due to unauthenticated access on non-public page');
      router.push('/admin/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated && !['/admin/login', '/admin/register'].includes(typeof window !== 'undefined' ? window.location.pathname : '')) {
    return null;
  }

  return <>{children}</>;
}