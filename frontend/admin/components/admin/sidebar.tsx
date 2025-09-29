'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  Stethoscope, 
  Building2, 
  Calendar, 
  BarChart3, 
  Settings,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';
import Image from 'next/image';
import Icon from '@/app/public/icon.png';
import { useAppContext } from '@/app/context/AppContext';

const navigation = [
  { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'Doctors', href: '/admin/doctors', icon: UserCheck },
  { name: 'Patients', href: '/admin/patients', icon: Users },
  { name: 'Services', href: '/admin/services', icon: Stethoscope },
  { name: 'Clinics', href: '/admin/clinics', icon: Building2 },
  { name: 'Appointments', href: '/admin/appointments', icon: Calendar },
  { name: 'Statistics', href: '/admin/statistics', icon: BarChart3 },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { userRole } = useAppContext();

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-md bg-white shadow-md border border-gray-200"
        >
          {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed top-0 left-0 z-40 h-screen w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center">
                <Image
                  src={Icon}
                  alt="QR Code"
                  width={128}
                  height={128}
                  unoptimized
                />
              </div>
              <span className="ml-2 text-xl font-bold uppercase text-gray-900">{`XTP - ${userRole || 'Guest'}`}</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-50 text-blue-700 border-r-2 border-blue-700"
                      : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <item.icon className={cn(
                    "mr-3 h-5 w-5",
                    isActive ? "text-blue-700" : "text-gray-400"
                  )} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </>
  );
}