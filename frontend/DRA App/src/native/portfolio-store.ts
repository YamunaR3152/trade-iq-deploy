import AsyncStorage from "@react-native-async-storage/async-storage";
import type { PortfolioSetup, Position } from "./types";

export type PortfolioDraft = {
  setup: PortfolioSetup;
  positions: Position[];
  updatedAt: string;
};

const PORTFOLIO_KEY = "dra.portfolioDrafts";
let memoryDrafts: Record<string, PortfolioDraft> = {};

function hasStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function normalizeStudentId(studentId: string) {
  return studentId.trim().replace(/\s+/g, "").toUpperCase();
}

async function readDrafts() {
  if (!hasStorage()) {
    try {
      const stored = await AsyncStorage.getItem(PORTFOLIO_KEY);
      memoryDrafts = stored ? (JSON.parse(stored) as Record<string, PortfolioDraft>) : {};
      return memoryDrafts;
    } catch {
      return memoryDrafts;
    }
  }

  try {
    return JSON.parse(window.localStorage.getItem(PORTFOLIO_KEY) || "{}") as Record<string, PortfolioDraft>;
  } catch {
    return memoryDrafts;
  }
}

async function writeDrafts(drafts: Record<string, PortfolioDraft>) {
  memoryDrafts = drafts;
  if (!hasStorage()) {
    await AsyncStorage.setItem(PORTFOLIO_KEY, JSON.stringify(drafts));
    return;
  }
  window.localStorage.setItem(PORTFOLIO_KEY, JSON.stringify(drafts));
}

export async function getPortfolioDraft(studentId: string) {
  const drafts = await readDrafts();
  return drafts[normalizeStudentId(studentId)] || null;
}

export async function savePortfolioDraft(studentId: string, setup: PortfolioSetup, positions: Position[]) {
  const key = normalizeStudentId(studentId);
  const drafts = await readDrafts();
  const draft = {
    setup: { ...setup, studentId: key },
    positions: positions.map((position) => ({ ...position, studentId: key })),
    updatedAt: new Date().toISOString(),
  };
  await writeDrafts({ ...drafts, [key]: draft });
  return draft;
}
