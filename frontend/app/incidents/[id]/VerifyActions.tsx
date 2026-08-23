"use client";

import { useState } from "react";
import { verifyHeal } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ShieldCheck, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

export function VerifyActions({ incidentId }: { incidentId: number }) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAction = async () => {
    setLoading(true);
    try {
      await verifyHeal(incidentId);
      // Wait a moment for background worker to process (demo effect)
      setTimeout(() => {
        router.refresh();
      }, 1500);
    } catch (error) {
      console.error(error);
      alert("Failed to verify recovery.");
      setLoading(false);
    }
  };

  return (
    <Card className="bg-card border-border shadow-sm">
      <CardContent className="p-4 sm:p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Verify Recovery</h3>
          <p className="text-sm text-muted-foreground font-mono mt-1">Run an immediate test to ensure the patched parser passes all constraints.</p>
        </div>
        <div className="flex w-full sm:w-auto">
          <Button 
            className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground transition-all"
            onClick={handleAction}
            disabled={loading}
          >
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ShieldCheck className="w-4 h-4 mr-2" />}
            {loading ? "Verifying..." : "Run Verification"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
