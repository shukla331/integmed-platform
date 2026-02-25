'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/useAuthStore'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (isMounted && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isMounted, router])

  // Avoid hydration mismatch and flash of protected content
  if (!isMounted) {
    return null
  }

  // While redirecting, render nothing
  if (!isAuthenticated) return null

  return <>{children}</>
}