import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-[10px] border border-transparent font-[600] whitespace-nowrap transition-all outline-none select-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-[#E11D48] text-white hover:bg-[#BE123C] active:bg-[#9F1239] shadow-[0_2px_8px_rgba(225,29,72,0.15)]",
        outline: "border border-[#E5E7EB] bg-white text-[#111827] hover:bg-[#F8FAFC] active:bg-[#F1F5F9] shadow-sm",
        secondary: "bg-[#F4F4F5] text-[#111827] hover:bg-[#E5E7EB] active:bg-[#D4D4D8]",
        ghost: "hover:bg-[#F8FAFC] text-[#64748B] hover:text-[#111827] active:bg-[#F1F5F9]",
        destructive: "bg-red-500 text-white hover:bg-red-600 active:bg-red-700",
        link: "text-[#111827] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-[40px] px-[18px] text-[13px] gap-2",
        sm: "h-[36px] px-[14px] text-[13px] gap-2",
        lg: "h-[48px] px-[24px] text-[14px] gap-2",
        icon: "h-[40px] w-[40px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
