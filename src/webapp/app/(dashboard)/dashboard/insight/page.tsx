"use client"

import { useState, useRef, ChangeEvent } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PenIcon, Check, Upload, Pencil, Trash2 } from 'lucide-react'
import Link from "next/link"
import { useToast } from "@/hooks/use-toast"
import { Separator } from "@/components/ui/separator"
import { ComingSoonWrapper } from "@/components/ComingSoonWrapper"

// Mock data
const mockJournalClubData = {
  pdfQueue: [
    { id: 1, title: "Advances in Quantum Computing", file: "quantum-computing.pdf" },
    { id: 2, title: "Neural Networks in Medicine", file: "neural-networks-medicine.pdf" },
  ],
}

interface PDF {
  id: number;
  title: string;
  file: File | null;
}

export default function JournalClubPage() {
  const [pdfTitle, setPdfTitle] = useState("")
  const [pdfQueue, setPdfQueue] = useState<PDF[]>(mockJournalClubData.pdfQueue.map(pdf => ({ ...pdf, file: null })))
  const [editingId, setEditingId] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handlePdfUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === "application/pdf") {
      const newPdf: PDF = { id: Date.now(), title: file.name, file: file }
      setPdfQueue([...pdfQueue, newPdf])
      toast({
        title: "PDF Uploaded",
        description: "Your PDF has been added to the queue.",
      })
    } else {
      toast({
        title: "Invalid File",
        description: "Please upload a PDF file.",
        variant: "destructive",
      })
    }
  }

  const handleSaveChanges = () => {
    // Mock API call
    console.log("Saving changes:", { pdfQueue })
    toast({
      title: "Settings Saved",
      description: "Your podcast settings have been updated.",
    })
  }

  const handleDeletePdf = (id: number) => {
    setPdfQueue(pdfQueue.filter(pdf => pdf.id !== id))
    toast({
      title: "PDF Deleted",
      description: "The PDF has been removed from the queue.",
    })
  }

  const handleEditTitle = (id: number, newTitle: string) => {
    setPdfQueue(pdfQueue.map(pdf => 
      pdf.id === id ? { ...pdf, title: newTitle } : pdf
    ))
    setEditingId(null)
    toast({
      title: "Title Updated",
      description: "The PDF title has been updated.",
    })
  }

  const startEditing = (id: number) => {
    setEditingId(id)
  }

  return (
    //<ComingSoonWrapper demo = '/demo/insight'>
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-black">Insight</h1>
      <p className="text-black">Listen to expert analyses of your documents and their applications to your interests.</p>
      <Separator className="my-6" />
      <Card className="bg-black bg-opacity-10 border-none">
        <CardHeader>
          <CardTitle className="text-black">Podcast Settings</CardTitle>
          <p className="text-black">An insight podcast will be automatically generated every morning that you have credits and there is a queue.</p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-end space-x-2">
              <div className="flex-grow space-y-2">
                <label htmlFor="pdf-title" className="text-black font-semibold">PDF Title</label>
                <Input
                  id="pdf-title"
                  value={pdfTitle}
                  onChange={(e) => setPdfTitle(e.target.value)}
                  placeholder="Enter PDF title"
                  className="bg-slate-600/30 border-gray-200/50 text-black"
                />
              </div>
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="bg-gray-400 hover:bg-gray-500 text-black"
              >
                <Upload className="mr-2 h-4 w-4" /> Upload PDF
              </Button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handlePdfUpload}
                accept=".pdf"
                style={{ display: 'none' }}
              />
            </div>
            {pdfQueue.length > 0 && (
              <Card className="bg-slate-600/30 border-gray-200/50">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-black">PDF Queue</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px] w-full rounded-md border border-gray-200/50">
                    {pdfQueue.map((pdf) => (
                      <div key={pdf.id} className="flex items-center justify-between p-4 border-b border-gray-200/30 last:border-b-0">
                        <div>
                          {editingId === pdf.id ? (
                            <Input
                              value={pdf.title}
                              onChange={(e) => handleEditTitle(pdf.id, e.target.value)}
                              onBlur={() => setEditingId(null)}
                              autoFocus
                              className="bg-slate-600/30 border-gray-200/50 text-black"
                            />
                          ) : (
                            <h4 className="text-sm font-medium text-black font-semibold">{pdf.title}</h4>
                          )}
                          <p className="text-sm text-gray-700">{pdf.file ? pdf.file.name : 'No file uploaded'}</p>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-black hover:text-black hover:bg-gray-200"
                            onClick={() => startEditing(pdf.id)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-red-400 hover:text-black hover:bg-red-900"
                            onClick={() => handleDeletePdf(pdf.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
            <div className="flex space-x-2">
              <Link href="/dashboard/edit-keywords">
                <Button variant="outline" className="bg-slate-600/30 text-black hover:bg-gray-200">
                  <PenIcon className="mr-2 h-4 w-4" /> Edit Interests
                </Button>
              </Link>
              <Button onClick={handleSaveChanges}  className="bg-gray-700 text-gray-100 hover:bg-gray-400">
                <Check className="mr-2 h-4 w-4" /> Save Changes
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
    //</ComingSoonWrapper>
  )
}

