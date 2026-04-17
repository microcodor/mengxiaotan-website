import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date, formatStr: string = 'yyyy-MM-dd HH:mm') {
  return format(new Date(date), formatStr, { locale: zhCN })
}

export function getCategoryName(category: string): string {
  const map: Record<string, string> = {
    ndrc: '发改委',
    coal: '煤炭',
    power: '电力',
    new_energy: '新能源',
  }
  return map[category] || category
}
