import { ContactForm } from './ContactForm'

export default function ContactPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
      <h1 className="text-3xl font-bold text-black mb-6">Contact Us</h1>
      <p className="text-xl text-gray-800 mb-8">We'd love to hear what you think of Auxiom</p>
      <ContactForm />
      </div>
    </div>
  )
}
