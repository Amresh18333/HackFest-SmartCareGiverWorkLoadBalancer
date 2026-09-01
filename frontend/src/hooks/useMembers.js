import { useState, useEffect, useCallback } from 'react'
import { api } from '../lib/api'

export function useMembers() {
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const fetchMembers = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api.getMembers()
      setMembers(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])
  
  useEffect(() => {
    fetchMembers()
  }, [fetchMembers])
  
  return { members, loading, error, refetch: fetchMembers }
}

export function useMember(memberId) {
  const [member, setMember] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const fetchMember = useCallback(async () => {
    if (!memberId) return
    try {
      setLoading(true)
      const data = await api.getMember(memberId)
      setMember(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [memberId])
  
  useEffect(() => {
    fetchMember()
  }, [fetchMember])
  
  return { member, loading, error, refetch: fetchMember }
}