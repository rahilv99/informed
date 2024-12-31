"use client";

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { updateUserNameOccupation } from '@/lib/actions';
import { toast } from "@/hooks/use-toast"
import { useRouter } from 'next/navigation';

const nameOccupationSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  occupation: z.string().min(2, {
    message: "Occupation must be at least 2 characters.",
  }),
})

type NameOccupationValues = z.infer<typeof nameOccupationSchema>

export function NameOccupation() {
  const router = useRouter();
  const form = useForm<NameOccupationValues>({
    resolver: zodResolver(nameOccupationSchema),
    defaultValues: {
      name: "",
      occupation: "",
    },
  })

  async function onSubmit(data: NameOccupationValues) {
    try {
      await updateUserNameOccupation(data);
      toast({
        title: "Information updated",
        description: "Your name and occupation have been saved.",
      })
      router.push('/keywords');
    } catch (error) {
      toast({
        title: "Error",
        description: "There was a problem saving your information.",
        variant: "destructive",
      })
    }
  }

  return (
    <main className="py-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="bg-black bg-opacity-10 text-black">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-black">Tell us about yourself</CardTitle>
            <CardDescription className="text-base text-gray-700">We'd like to know a bit more about you.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Your name" {...field} />
                      </FormControl>
                      <FormDescription>
                        This will only be used to address you in our communications.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="occupation"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Occupation</FormLabel>
                      <FormControl>
                        <Input placeholder="Your occupation" {...field} />
                      </FormControl>
                      <FormDescription>
                        This helps us tailor content to your professional needs.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button 
                  type="submit"
                  className="w-full bg-gray-800 text-white px-4 py-2 rounded-full font-semibold hover:bg-gray-600 transition duration-300"
                >
                  Next
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

