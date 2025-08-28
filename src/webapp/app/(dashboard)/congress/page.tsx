import { getRecommendedBills, getUser } from '@/lib/db/queries';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Calendar, FileText, Database, Clock, HardDrive, Star, TrendingUp } from 'lucide-react';

interface CongressBill {
  id: number;
  billId: string;
  title: string;
  url?: string;
  latestActionDate?: string;
  latestActionText?: string;
  congress?: number;
  billType?: string;
  billNumber?: number;
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
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Please log in to view personalized bills</h3>
          <p className="text-gray-500">
            You need to be logged in with a complete profile to see bills tailored to your interests.
          </p>
        </div>
      </div>
    );
  }

  const recommendedBills = await getRecommendedBills(user.embedding) as unknown as CongressBill[];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recommended Congress Bills</h1>
        <p className="text-gray-600">
          Congressional bills personalized for your interests, ranked by relevance.
        </p>
      </div>

      {recommendedBills.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No bills found</h3>
          <p className="text-gray-500">
            No congressional bills have been scraped yet. Check back later.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Database className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Bills</p>
                    <p className="text-2xl font-bold text-gray-900">{recommendedBills.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Star className="h-8 w-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Top Match</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendedBills.length > 0 ? formatDistance(recommendedBills[0].distance) : 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <TrendingUp className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Congress</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendedBills.length > 0 ? `${recommendedBills[0].congress}th` : 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Bills List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Your Personalized Bills</h2>
            
            <div className="grid gap-4">
              {recommendedBills.map((bill, index) => (
                <Card key={bill.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg leading-tight mb-2 flex items-center gap-2">
                          <FileText className="h-5 w-5 text-blue-600" />
                          {bill.title}
                          {index === 0 && (
                            <Badge variant="default" className="bg-yellow-100 text-yellow-800">
                              <Star className="h-3 w-3 mr-1" />
                              Best Match
                            </Badge>
                          )}
                          <Badge variant="outline" className="text-xs">
                            {formatDistance(bill.distance)} match
                          </Badge>
                        </CardTitle>
                        <CardDescription className="flex items-center gap-4 flex-wrap">
                          <span className="flex items-center gap-1">
                            <Database className="h-4 w-4" />
                            {bill.billId}
                          </span>
                          <span className="flex items-center gap-1">
                            <FileText className="h-4 w-4" />
                            {formatBillType(bill.billType)}
                          </span>
                          {bill.latestActionDate && (
                            <span className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatActionDate(bill.latestActionDate)}
                            </span>
                          )}
                        </CardDescription>
                      </div>
                      {bill.url && (
                        <a
                          href={bill.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                        >
                          <ExternalLink className="h-4 w-4" />
                          View Bill
                        </a>
                      )}
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-3">
                      {bill.latestActionText && (
                        <div>
                          <span className="text-sm font-medium text-gray-700">Latest Action:</span>
                          <p className="text-sm text-gray-600 mt-1">
                            {bill.latestActionText}
                          </p>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs text-gray-500 pt-2 border-t">
                        <span>Bill #{bill.billNumber}</span>
                        <span>•</span>
                        <span>{bill.congress}th Congress</span>
                        <span>•</span>
                        <span>Relevance: {formatDistance(bill.distance)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
