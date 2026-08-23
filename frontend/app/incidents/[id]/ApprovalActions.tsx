"use client";

import { useState } from "react";
import { approveHeal } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Check, X, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

export function ApprovalActions({ incidentId }: { incidentId: number }) {
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const router = useRouter();

  const handleAction = async (approved: boolean) => {
    setLoading(approved ? "approve" : "reject");
    try {
      await approveHeal(incidentId, approved);
      // Wait a moment for background worker to process (demo effect)
      setTimeout(() => {
        router.refresh();
      }, 1000);
    } catch (error) {
      console.error(error);
      alert("Failed to submit action.");
      setLoading(null);
    }
  };

  return (
    <Card className="bg-card border-border shadow-sm">
      <CardContent className="p-4 sm:p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Human Approval Required</h3>
          <p className="text-sm text-muted-foreground font-mono mt-1">Review the AI recovery patch above before deploying to production.</p>
        </div>
        <div className="flex gap-3 w-full sm:w-auto">
          <Button 
            variant="outline" 
            className="flex-1 sm:flex-none border-destructive/50 text-destructive hover:bg-destructive/10 hover:text-destructive"
            onClick={() => handleAction(false)}
            disabled={loading !== null}
          >
            {loading === "reject" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <X className="w-4 h-4 mr-2" />}
            Reject Fix
          </Button>
          <Button 
            className="flex-1 sm:flex-none bg-emerald-500 hover:bg-emerald-600 text-white transition-all"
            onClick={() => handleAction(true)}
            disabled={loading !== null}
          >
            {loading === "approve" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-2" />}
            Approve & Deploy
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
