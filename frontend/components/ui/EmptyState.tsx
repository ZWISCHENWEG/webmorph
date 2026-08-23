import React from 'react';
import { Card } from './card';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: React.ReactNode;
  action?: React.ReactNode;
  children?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action, children }: EmptyStateProps) {
  return (
    <Card className="max-w-[900px] min-h-[500px] w-full mx-auto flex flex-col items-center justify-center text-center p-12">
      {children}
      {!children && (
        <>
          {icon && (
            <div className="w-16 h-16 rounded-full bg-[#F8FAFC] border border-[#E5E7EB] flex items-center justify-center mb-6 shadow-sm text-[#64748B] [&_svg]:w-8 [&_svg]:h-8">
              {icon}
            </div>
          )}
          {title && <h3 className="text-[18px] font-[700] text-[#111827] mb-2">{title}</h3>}
          {description && (
            <div className="text-[14px] text-[#64748B] max-w-md mx-auto mb-6 leading-relaxed">
              {description}
            </div>
          )}
          {action}
        </>
      )}
    </Card>
  );
}
