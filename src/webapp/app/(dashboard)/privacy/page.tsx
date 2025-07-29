import { readFileSync } from 'fs'
import { join } from 'path'

function getPrivacyPolicyContent() {
  const filePath = join(process.cwd(), 'public', 'policy.html')
  return readFileSync(filePath, 'utf8')
}

export default function PrivacyPage() {
  const policyContent = getPrivacyPolicyContent()
  
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <div 
          className="prose prose-sm max-w-4xl mx-auto"
          dangerouslySetInnerHTML={{ __html: policyContent }}
        />
      </div>
    </div>
  )
}
