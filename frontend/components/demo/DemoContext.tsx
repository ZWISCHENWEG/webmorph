"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type DemoStage = "READY" | "DETECTED" | "ANALYZING" | "APPROVAL" | "HEALING" | "RECOVERED";

type DemoState = {
  demoStage: DemoStage;
  startDemo: () => void;
  approveRepair: () => void;
  resetDemo: () => void;
};

const DemoContext = createContext<DemoState | null>(null);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [demoStage, setDemoStage] = useState<DemoStage>("READY");

  const startDemo = () => {
    setDemoStage("DETECTED");
    setTimeout(() => setDemoStage("ANALYZING"), 3000);
    setTimeout(() => setDemoStage("APPROVAL"), 6000);
  };

  const approveRepair = () => {
    setDemoStage("HEALING");
    setTimeout(() => setDemoStage("RECOVERED"), 3000);
  };

  const resetDemo = () => {
    setDemoStage("READY");
  };

  useEffect(() => {
    resetDemo();
  }, []);

  return (
    <DemoContext.Provider value={{ demoStage, startDemo, approveRepair, resetDemo }}>
      {children}
    </DemoContext.Provider>
  );
}

export const useDemo = () => {
  const ctx = useContext(DemoContext);
  if (!ctx) return { demoStage: "READY" as DemoStage, startDemo: () => {}, approveRepair: () => {}, resetDemo: () => {} };
  return ctx;
};
