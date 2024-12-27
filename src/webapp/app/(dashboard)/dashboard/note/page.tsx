"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Checkbox } from "@/components/ui/checkbox"
import { PlusCircle, X, Edit2, Podcast, Check } from 'lucide-react'
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ComingSoonWrapper } from "@/components/ComingSoonWrapper"  

// Mock data
const mockNotes = [
  { id: 1, content: "Review latest paper on quantum entanglement", isComplete: true, isSelected: false },
  { id: 2, content: "Prepare questions for next journal club meeting", isComplete: true, isSelected: true },
  { id: 3, content: "Summarize findings from neural network experiment", isComplete: true, isSelected: false },
]
const credits = 3

export default function NotesPage() {
  const [notes, setNotes] = useState(mockNotes)
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null)

  const addNewNote = () => {
    const newNote = { id: Date.now(), content: "", isComplete: false, isSelected: false }
    setNotes([...notes, newNote])
    setEditingNoteId(newNote.id)
  }

interface Note {
    id: number
    content: string
    isComplete: boolean
    isSelected: boolean
}

const handleNoteChange = (id: number, value: string) => {
    setNotes(notes.map((note: Note) =>
        note.id === id ? { ...note, content: value } : note
    ))
}

const completeNote = (id: number) => {
    setNotes(notes.map((note: Note) =>
        note.id === id ? { ...note, isComplete: true } : note
    ).filter(note => note.id !== id || note.content.trim() !== ""))
    setEditingNoteId(null)
    exportToBackend();
}

const removeNote = (id: number) => {
  setNotes(notes.filter(note => note.id !== id));
  exportToBackend();
  if (editingNoteId === id) {
    setEditingNoteId(null);
  }
}

const completeEditingNote = (id: number) => {
  setNotes(notes.map(note =>
    note.id === id ? { ...note, isComplete: true } : note
  ));
  setEditingNoteId(null);
  exportToBackend();
}

const toggleNoteSelection = (id: number) => {
    const selectedCount = notes.filter((note: Note) => note.isSelected).length
    setNotes(notes.map((note: Note) => {
        if (note.id === id) {
            if (!note.isSelected && selectedCount >= 3) {
                return note
            }
            return { ...note, isSelected: !note.isSelected }
        }
        return note
    }))
}

  const selectedNotes = notes.filter(note => note.isSelected)

  const exportToBackend = () => {
    console.log('Exporting notes to backend:', notes);
    // In a real application, you would make an API call here
  }

  return (
    //<ComingSoonWrapper demo = '/demo/note'>
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-black">Notes</h1>
      <p className="text-black">Get a daily podcast of everything you're curious about.</p>
      <Separator className="my-6" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="col-span-1 md:col-span-2 bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle>
            <div className="flex items-center justify-between text-black">
              <span>Your Notes</span>
              <Button onClick={addNewNote} variant="ghost" size="icon" className="text-black hover:text-black hover:bg-gray-200">
                <PlusCircle className="h-5 w-5" />
              </Button>
              </div>
            </CardTitle>
            <p className="text-black">A notes podcast will be automatically generated every morning that you have credits and there are notes selected.</p>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[50vh] pr-4">
              {notes.map((note) => (
                <div key={note.id} className="mb-4 group relative">
                  <div className={`p-3 pl-4 rounded-md transition-all duration-200 flex items-center ${
                    note.isComplete ? 'bg-slate-600/30' : 'bg-cyan-900/10'
                  }`}>
                    {note.isComplete && (
                      <Checkbox
                        checked={note.isSelected}
                        onCheckedChange={() => toggleNoteSelection(note.id)}
                        className="mr-2 border-gray-500"
                      />
                    )}
                    {editingNoteId === note.id ? (
                      <Textarea
                        value={note.content}
                        onChange={(e) => handleNoteChange(note.id, e.target.value)}
                        onBlur={() => completeNote(note.id)}
                        className="min-h-[70px] bg-transparent text-black border-none focus:ring-0"
                        autoFocus
                      />
                    ) : (
                      <p className="text-black">{note.content}</p>
                    )}
                  </div>
                  {note.isComplete && 
                  editingNoteId !== note.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-black hover:text-black hover:bg-gray-200"
                      onClick={() => removeNote(note.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                  {editingNoteId === note.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-black hover:text-black hover:bg-gray-200"
                      onClick={() => completeEditingNote(note.id)}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  )}
                  {note.isComplete && editingNoteId !== note.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-10 opacity-0 group-hover:opacity-100 transition-opacity text-black hover:text-black hover:bg-gray-200"
                      onClick={() => setEditingNoteId(note.id)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </ScrollArea>
          </CardContent>
        </Card>
        <Card className="bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle className="flex items-center text-black">
              <Podcast className="mr-2 h-5 w-5" />
              Upcoming Podcast
            </CardTitle>
            <p className="mt-4 text-black">Credits remaining: {credits}</p>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-black">Topics ({selectedNotes.length}/3)</p>
            <div className="space-y-2">
              {selectedNotes.map((note) => (
                <div key={note.id} className="flex items-center justify-between p-2 rounded">
                  <Badge variant="secondary" className="text-sm bg-gray-700 bg-opacity-20 text-black">
                    {note.content.length > 40 ? note.content.substring(0, 40) + '...' : note.content}
                  </Badge>
                </div>
              ))}
              {selectedNotes.length === 0 && (
                <p className="text-sm text-black">No topics selected for the upcoming podcast.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
    //</ComingSoonWrapper>
  )
}

