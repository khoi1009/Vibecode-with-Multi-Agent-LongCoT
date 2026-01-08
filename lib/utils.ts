import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twxMerge(clsx(inputs)) // Using twMerge for Tailwind class conflicts
}
