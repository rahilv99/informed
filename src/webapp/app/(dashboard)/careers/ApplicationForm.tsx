'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { sendApplication } from './actions'

export function ApplicationForm() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [position, setPosition] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      await sendApplication(name, email, position, message)
      toast({
        title: "Application sent",
        description: "Thank you for your interest in joining Auxiom!",
      })
      setName('')
      setEmail('')
      setPosition('')
      setMessage('')
    } catch (error) {
      toast({
        title: "Error",
        description: "There was a problem sending your application. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-800 mb-2">
          Name
        </label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full bg-gray-700 bg-opacity-10 border-gray-900 text-black"
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-800 mb-2">
          Email
        </label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full bg-gray-700 bg-opacity-10 border-gray-900 text-black"
        />
      </div>
      <div>
        <label htmlFor="position" className="block text-sm font-medium text-gray-800 mb-2">
          Position
        </label>
        <Input
          id="position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          required
          className="w-full bg-gray-700 bg-opacity-10 border-gray-900 text-black"
        />
      </div>
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-800 mb-2">
          Cover Letter
        </label>
        <Textarea
          id="message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
          className="w-full bg-gray-700 bg-opacity-10 border-gray-900 text-black min-h-[150px]"
        />
      </div>
      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-gray-800 hover:bg-gray-600 text-white rounded-xl"
      >
        {isSubmitting ? 'Sending...' : 'Apply'}
      </Button>
    </form>
  )
}

