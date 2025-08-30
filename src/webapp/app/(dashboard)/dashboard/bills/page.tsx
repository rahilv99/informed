import { getRecommendedBills, getUser } from '@/lib/db/queries';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Calendar, FileText, Clock, Star, Search } from 'lucide-react';

interface CongressBill {
  id: number;
  bill_id: string;
  title: string;
  url?: string;
  latest_action_date?: string;
  latest_action_text?: string;
  congress?: number;
  bill_type?: string;
  bill_number?: number;
  embedding: number[];
  distance: number;
}

function formatDistance(distance: number): string {
  // Convert distance to similarity percentage (lower distance = higher similarity)
  const similarity = Math.max(0, (1 - distance) * 100);
  return `${similarity.toFixed(1)}%`;
}

function formatBillType(billType?: string): string {
  if (!billType) return 'Unknown';
  
  const typeMap: { [key: string]: string } = {
    'hr': 'House Bill',
    's': 'Senate Bill',
    'hjres': 'House Joint Resolution',
    'sjres': 'Senate Joint Resolution',
    'hconres': 'House Concurrent Resolution',
    'sconres': 'Senate Concurrent Resolution',
    'hres': 'House Resolution',
    'sres': 'Senate Resolution'
  };
  
  return typeMap[billType.toLowerCase()] || billType.toUpperCase();
}

function formatActionDate(dateString?: string): string {
  if (!dateString) return 'Unknown';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

export default async function CongressPage() {
  const user = await getUser();
  
  if (!user || !user.embedding) {
    return (
      <div className="min-h-screen">
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground opacity-50 mb-4" />
              <h3 className="text-lg font-medium mb-2">Please log in to view personalized bills</h3>
              <p className="text-muted-foreground">
                You need to be logged in with a complete profile to see bills tailored to your interests.
              </p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const recommendedBills = await getRecommendedBills(user.embedding) as unknown as CongressBill[];

  return (
    <div className="min-h-screen py-6 sm:py-12 px-2 sm:px-4">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-2">
            {user?.name?.split(" ")[0]}'s Bills
          </h1>
          <p className="text-gray-600">
            Bills personalized for your interests, ranked by relevance.
          </p>
          {recommendedBills.length > 0 && (
            <div className="text-sm text-gray-500 mt-2">
              Showing {recommendedBills.length} {recommendedBills.length === 1 ? 'bill' : 'bills'}
              {recommendedBills.length > 0 && (
                <> • Top match: {formatDistance(recommendedBills[0].distance)}</>
              )}
              {recommendedBills.length > 0 && recommendedBills[0].latest_action_date && (
                <> • Last updated: {formatActionDate(recommendedBills[0].latest_action_date)}</>
              )}
            </div>
          )}
        </div>
        <div className="border-b border-gray-200 mb-6"></div>

        <div className="space-y-6">
          {recommendedBills.length === 0 ? (
            <div className="text-center py-12">
              <div className="flex flex-col items-center justify-center py-8 space-y-4">
                <div className="rounded-full bg-gray-100 p-4">
                  <Search className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-medium text-gray-800">No bills found</h3>
                <p className="text-gray-600 max-w-md">
                  No congressional bills have been scraped yet. Check back soon for new content!
                </p>
              </div>
            </div>
          ) : (
            recommendedBills.map((bill, index) => (
              <div
                key={bill.id}
                className="backdrop-blur-lg bg-black bg-opacity-10 border border-gray-100 overflow-hidden shadow-md hover:shadow-lg transition-shadow p-6 rounded-lg"
              >
                <div className="space-y-4">
                  {/* Title and Match Score */}
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-bold leading-tight hover:text-primary transition-colors text-lg md:text-xl flex-1 text-gray-800">
                        {bill.title}
                      </h3>
                      {bill.url && (
                        <a
                          href={bill.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-primary hover:text-primary/80 text-sm shrink-0"
                        >
                          <ExternalLink className="h-4 w-4" />
                          View Bill
                        </a>
                      )}
                    </div>
                    
                    {/* Match percentage badge */}
                    <div>
                      <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/20">
                        {formatDistance(bill.distance)} match
                      </Badge>
                    </div>
                  </div>

                  {/* Bill Type and Date */}
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      {formatBillType(bill.bill_type)}
                    </span>
                    {bill.latest_action_date && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatActionDate(bill.latest_action_date)}
                      </span>
                    )}
                  </div>

                  {/* Latest Action */}
                  {bill.latest_action_text && (
                    <div className="space-y-2">
                      <span className="text-sm font-medium text-gray-800">Latest Action:</span>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {bill.latest_action_text}
                      </p>
                    </div>
                  )}

                  {/* Bill Meta - Clean divider style */}
                  <div className="flex items-center justify-between pt-4 mt-4 border-t border-gray-200">
                    <div className="text-xs text-gray-500">
                      {bill.bill_id || 'Unknown Bill'}
                    </div>
                    <div className="text-xs text-gray-500">
                      Relevance: {formatDistance(bill.distance)}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
