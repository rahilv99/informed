'use client'

import { useState, useEffect } from 'react'
import { Check, Upload, ArrowLeft, Pencil, Trash2, UserPen } from 'lucide-react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import Link from 'next/link'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { Switch } from "@/components/ui/switch"
import { motion } from "framer-motion"

export default function PodcastSettings() {
  const [podcastType, setPodcastType] = useState("updates")
  const [pdfQueue, setPdfQueue] = useState<PdfFile[]>([])
  const [pdfTitle, setPdfTitle] = useState("")
  const [editingPdf, setEditingPdf] = useState<PdfFile | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [defaultType, setDefaultType] = useState("updates")
  const { toast } = useToast()

  useEffect(() => {
    if (pdfQueue.length > 0 && defaultType === "updates") {
      setDefaultType("journal-club")
    }
  }, [pdfQueue])

interface PdfFile {
    title: string;
    file: string;
}

interface PdfUploadEvent extends React.ChangeEvent<HTMLInputElement> {}

const handlePdfUpload = (event: PdfUploadEvent): void => {
    const file = event.target.files?.[0];
    if (file && pdfTitle) {
        const newPdf: PdfFile = { title: pdfTitle, file: file.name };
        setPdfQueue([...pdfQueue, newPdf]);
        setPdfTitle("");
        toast({
            title: "PDF Uploaded",
            description: `${file.name} has been added to the queue.`,
        });
    }
}

interface EditPdfHandler {
    (index: number, newTitle: string, newFileName: string): void;
}

const handleEditPdf: EditPdfHandler = (index, newTitle, newFileName) => {
    const updatedQueue = [...pdfQueue];
    updatedQueue[index] = { ...updatedQueue[index], title: newTitle, file: newFileName };
    setPdfQueue(updatedQueue);
    setIsDialogOpen(false);
    toast({
        title: "PDF Updated",
        description: "The PDF details have been updated successfully.",
    });
};

interface DeletePdfHandler {
    (index: number): void;
}

const handleDeletePdf: DeletePdfHandler = (index) => {
    const updatedQueue = pdfQueue.filter((_, i) => i !== index);
    setPdfQueue(updatedQueue);
    toast({
        title: "PDF Removed",
        description: "The PDF has been removed from the queue.",
        variant: "destructive",
    });
};

interface Pdf {
    title: string;
    file: string;
}

interface Toast {
    title: string;
    description: string;
    variant?: string;
}

const handleDefaultTypeChange_1 = (checked: boolean) => {
    const newDefaultType: string = checked ?  "journal-club" : "updates";
    setDefaultType(newDefaultType);
    toast({
        title: "Default Updated",
        description: `${newDefaultType} is now set as the default podcast type.`,
    });
};

const handleDefaultTypeChange_2 = (checked: boolean) => {
    const newDefaultType: string = checked ?  "updates" : "journal-club";
    setDefaultType(newDefaultType);
    toast({
        title: "Default Updated",
        description: `${newDefaultType} is now set as the default podcast type.`,
    });
};

  return (
    <div className="min-h-screen text-white p-8">
      <Card className="max-w-4xl mx-auto bg-white bg-opacity-10 border-none">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-3xl font-bold text-cyan-200">Podcast Preferences</CardTitle>
            <Link href="/dashboard">
              <Button variant="ghost" className="text-cyan-200 hover:text-white hover:bg-cyan-800">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
              </Button>
            </Link>
          </div>
          <CardDescription className="text-gray-300 mt-2">
            Customize your podcast experience. Choose between Journal Club and Updates, and manage your PDF queue for Journal Club sessions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">

          <Tabs defaultValue={podcastType} onValueChange={setPodcastType} className="w-full">
            <TabsList className="flex justify-center items-center w-full mx-auto h-14 rounded-lg bg-cyan-900/20 p-1 text-cyan-100 max-w-lg">
              <TabsTrigger value="updates" className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-10 data-[state=active]:bg-cyan-200 data-[state=active]:text-white data-[state=active]:shadow-sm data-[state=active]:bg-cyan-200 relative">
                Updates
                {podcastType === "updates" && (
                  <motion.div
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-200"
                    layoutId="underline"
                  />
                )}
              </TabsTrigger>
              <TabsTrigger value="journal-club" className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-10 data-[state=active]:bg-cyan-200 data-[state=active]:text-white data-[state=active]:shadow-sm data-[state=active]:bg-cyan-200 relative">
                Journal Club
                {podcastType === "journal-club" && (
                  <motion.div
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-200"
                    layoutId="underline"
                  />
                )}
              </TabsTrigger>
            </TabsList>
            <TabsContent value="updates" className="space-y-4">
                <div className="flex items-center space-x-2">
                    <Switch
                        id="updates"
                        checked={defaultType === "updates"}
                        onCheckedChange={handleDefaultTypeChange_2}
                        className="data-[state=checked]:bg-cyan-200"
                        />
                    <Label htmlFor="updates" className="text-white">Default</Label>
                </div>
              <Card className="bg-black bg-opacity-15 border-none">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-cyan-200">Updates Podcast</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300">
                  A personalized weekly podcast summarizing the latest updates in your field. All content includes citations to academic sources.
                  </p>
                </CardContent>
              </Card>

              <Link href="/dashboard/interests">
                <Button className="bg-cyan-200 hover:bg-cyan-600 text-black">
                <UserPen className="mr-2 h-4 w-4" /> Edit Interests
                </Button>
              </Link>
            </TabsContent>
            <TabsContent value="journal-club" className="space-y-4">
                
                <div className="flex items-center space-x-2">
                    <Switch
                        id="journal-club"
                        checked={defaultType === "journal-club"}
                        onCheckedChange={handleDefaultTypeChange_1}
                        className="data-[state=checked]:bg-cyan-200"
                        />
                    <Label htmlFor="journal-club" className="text-white">Default</Label>
                </div>
                
                <Card className="bg-black bg-opacity-15 border-none">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-cyan-200">Journal Club Podcast</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300">
                  Want your weekly podcast to be about something in particular? Queue up scientific papers or topics, and get expert summaries and analysis. After our analysis we'll look into the applications of the research in your field.
                  </p>
                </CardContent>
              </Card>

              <Link href="/dashboard/interests">
                <Button className="bg-cyan-200 hover:bg-cyan-600 text-black">
                <UserPen className="mr-2 h-4 w-4" /> Edit Interests
                </Button>
              </Link>
              <div className="flex items-end space-x-2">
                <div className="flex-grow space-y-4">
                  <Label htmlFor="pdf-title" className="text-cyan-200 mb-2 block">Queued Articles</Label>
                  <Input
                    id="pdf-title"
                    type="text"
                    placeholder="Enter PDF title"
                    value={pdfTitle}
                    onChange={(e) => setPdfTitle(e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                  />
                </div>
                <Input
                  id="pdf-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  className="hidden"
                />
                <Button
                  onClick={() => {
                    const pdfUploadElement = document.getElementById('pdf-upload');
                    if (pdfUploadElement) {
                      pdfUploadElement.click();
                    }
                  }}
                  className="bg-cyan-200 hover:bg-cyan-600 text-black"
                  disabled={!pdfTitle}
                >
                  <Upload className="mr-2 h-4 w-4" /> Upload PDF
                </Button>
              </div>
              {pdfQueue.length > 0 && (
                <Card className="bg-gray-700 border-gray-600">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold text-cyan-200">PDF Queue</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[200px] w-full rounded-md border border-gray-600">
                      {pdfQueue.map((pdf, index) => (
                        <div key={index} className="flex items-center justify-between p-4">
                          <div className="flex-grow">
                            <h4 className="text-sm font-medium text-white">{pdf.title}</h4>
                            <p className="text-sm text-gray-400">{pdf.file}</p>
                          </div>
                          <div className="flex space-x-2">
                            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                              <DialogTrigger asChild>
                                <Button variant="ghost" size="sm" className="text-cyan-200 hover:text-white hover:bg-cyan-800" onClick={() => setEditingPdf(pdf)}>
                                  <Pencil className="h-4 w-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-gray-800 text-white">
                                <DialogHeader>
                                  <DialogTitle className="text-cyan-200">Edit PDF Details</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4 pt-4">
                                  <div className="space-y-2">
                                    <Label htmlFor="edit-title" className="text-cyan-200">Title</Label>
                                    <Input
                                      id="edit-title"
                                      defaultValue={pdf.title}
                                      className="bg-gray-700 border-gray-600 text-white"
                                    />
                                  </div>
                                  <div className="space-y-2">
                                    <Label htmlFor="edit-filename" className="text-cyan-200">File Name</Label>
                                    <Input
                                      id="edit-filename"
                                      defaultValue={pdf.file}
                                      className="bg-gray-700 border-gray-600 text-white"
                                    />
                                  </div>
                                  <Button 
                                    className="w-full bg-cyan-600 hover:bg-cyan-700 text-white"
                                    onClick={() => handleEditPdf(
                                      index,
                                      (document.getElementById('edit-title') as HTMLInputElement)?.value || '',
                                      (document.getElementById('edit-filename') as HTMLInputElement)?.value || ''
                                    )}
                                  >
                                    Save Changes
                                  </Button>
                                </div>
                              </DialogContent>
                            </Dialog>
                            <Button variant="ghost" size="sm" className="text-red-400 hover:text-white hover:bg-red-900" onClick={() => handleDeletePdf(index)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                          {index < pdfQueue.length - 1 && <Separator className="my-2" />}
                        </div>
                      ))}
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>

          <Button className="w-full bg-cyan-300 hover:bg-cyan-600 text-black">
            <Check className="mr-2 h-4 w-4" /> Save Podcast Settings
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

