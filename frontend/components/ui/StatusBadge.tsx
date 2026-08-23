import * as React from "react"
import { cn } from "@/lib/utils"

interface StatusBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'success' | 'warning' | 'error' | 'neutral' | 'active';
  children: React.ReactNode;
}

export function StatusBadge({ variant = 'neutral', className, children, ...props }: StatusBadgeProps) {
  const variants = {
    success: 'bg-[#DCFCE7] text-[#166534] border-[#bbf7d0]',
    warning: 'bg-[#FEF3C7] text-[#92400E] border-[#fde68a]',
    error: 'bg-[#FFE4E6] text-[#BE123C] border-[#fecdd3]',
    neutral: 'bg-[#F4F4F5] text-[#71717A] border-[#e4e4e7]',
    active: 'bg-[#E11D48] text-white border-[#BE123C]'
  };

  return (
    <div
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
