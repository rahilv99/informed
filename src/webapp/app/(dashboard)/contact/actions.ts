'use server'

import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendContactForm({ subject, body }: { subject: string; body: string }) {
  try {
    await resend.emails.send({
      from: 'contact@yourdomain.com', // CHANGE BEFORE DEPLOYING
      to: 'rahilv99@gmail.com', // CHANGE BEFORE DEPLOYING
      subject: `New Contact Form Submission: ${subject}`,
      text: body,
    })
  } catch (error) {
    console.error('Error sending email:', error)
    throw new Error('Failed to send message')
  }
}
