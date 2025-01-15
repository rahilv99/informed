'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useToast } from '@/hooks/use-toast';
import { Input } from '@/components/ui/input'
import { sendContactForm } from '../../contact/actions';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Textarea } from '@/components/ui/textarea';

export default function ContactSalesPage() {

    const [email, setEmail] = useState('')
    const [company, setCompany] = useState('')
    const [body_text, setBody] = useState('')
    const [plan, setPlan] = useState('')
    const { toast } = useToast()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            const subject = `Auxiom Enterprise Sales: ${email} from ${company}`
            const body = `Plan: ${plan}\n\n${body_text}`
            await sendContactForm({ subject, body })
            toast({
                title: "Thank you for your inquiry.",
                description: "You can expect a response in the next 24 hours.",
            })
            setEmail('')
            setCompany('')
            setBody('')
            setPlan('')
        } catch (error) {
            toast({
                title: "Error",
                description: "There was a problem sending your message. Please try again.",
                variant: "destructive",
            })
        }
    }

    return (
        <main className="min-h-screen max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-3xl font-bold mb-6">Contact Auxiom Sales</h1>
            <p className="mb-8 text-gray-700">
                Thank you for your interest in Auxiom Enterprise. Please fill out the form below, and our sales team will get back to you shortly to discuss how we can tailor our solutions to your needs.
            </p>
            <form className="space-y-6">
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Contact
                    </label>
                    <Input
                        placeholder="e.g sales@auxiomai.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="bg-black bg-opacity-10 border-gray-800 text-black placeholder-gray-300 w-full rounded-md focus:ring-black"
                    />
                </div>
                <div>
                    <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                        Company / Institution
                    </label>
                    <Input
                        placeholder="e.g Auxiom AI"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        required
                        className="bg-black bg-opacity-10 border-gray-800 text-black placeholder-gray-300 w-full rounded-md focus:ring-black"
                    />
                </div>
                <div>
                    <label htmlFor="plan" className="block text-sm font-medium text-gray-700">
                        Plan
                    </label>

                    <Select name="plan" required onValueChange={(value) => setPlan(value)}>
                        <SelectTrigger className="bg-black bg-opacity-10 border-gray-800 text-black placeholder-gray-300 w-full rounded-md focus:ring-black">
                            <SelectValue placeholder="Select a plan" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Enterprise">Enterprise</SelectItem>
                            <SelectItem value="Academic Institutions">Academic Institutions</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700">
                        Message
                    </label>
                    <Textarea
                        placeholder="Your message"
                        value={body_text}
                        onChange={(e) => setBody(e.target.value)}
                        required
                        className="bg-black bg-opacity-10 border-gray-800 text-black placeholder-gray-300 min-h-[150px]"
                    />
                </div>
                <div>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-800 hover:bg-gray-800"
                    >
                        Send Message
                    </button>
                </div>
            </form>
        </main>
    );
}

