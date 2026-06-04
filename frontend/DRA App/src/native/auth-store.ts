import type { UserData } from "./types";
import AsyncStorage from "@react-native-async-storage/async-storage";

const USERS_KEY = "dra.studentProfiles";
const SESSION_KEY = "dra.activeStudentId";
let memoryUsers: UserData[] = [];
let memoryActiveStudentId = "";

function hasStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

async function readUsers(): Promise<UserData[]> {
  if (!hasStorage()) {
    try {
      const stored = await AsyncStorage.getItem(USERS_KEY);
      memoryUsers = stored ? (JSON.parse(stored) as UserData[]) : [];
      return memoryUsers;
    } catch {
      return memoryUsers;
    }
  }
  try {
    return JSON.parse(window.localStorage.getItem(USERS_KEY) || "[]") as UserData[];
  } catch {
    return memoryUsers;
  }
}

async function writeUsers(users: UserData[]) {
  memoryUsers = users;
  if (!hasStorage()) {
    await AsyncStorage.setItem(USERS_KEY, JSON.stringify(users));
    return;
  }
  window.localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function normalizeUserId(studentId: string) {
  return studentId.trim().replace(/\s+/g, "").toUpperCase();
}

export async function generateStudentId() {
  const users = await readUsers();
  const year = "2026";
  const next = users.reduce((max, user) => {
    if (!user.studentId.startsWith(year) || user.studentId.length !== 12) return max;
    const sequence = Number(user.studentId.slice(4));
    return Number.isFinite(sequence) ? Math.max(max, sequence) : max;
  }, 0) + 1;
  return `${year}${String(next).padStart(8, "0")}`;
}

export async function saveRegisteredUser(user: UserData) {
  const users = await readUsers();
  const normalizedUser = { ...user, studentId: normalizeUserId(user.studentId), password: user.password.trim() };
  const withoutDuplicate = users.filter((item) => normalizeUserId(item.studentId) !== normalizedUser.studentId && item.email.toLowerCase() !== normalizedUser.email.toLowerCase());
  await writeUsers([...withoutDuplicate, normalizedUser]);
  await setActiveStudentId(normalizedUser.studentId);
  return normalizedUser;
}

export async function signInUser(studentId: string, password: string) {
  const normalized = normalizeUserId(studentId);
  const normalizedPassword = password.trim();
  const users = await readUsers();
  return users.find((user) => normalizeUserId(user.studentId) === normalized && user.password.trim() === normalizedPassword) || null;
}

export async function setActiveStudentId(studentId: string) {
  memoryActiveStudentId = studentId;
  if (!hasStorage()) {
    await AsyncStorage.setItem(SESSION_KEY, studentId);
    return;
  }
  window.localStorage.setItem(SESSION_KEY, studentId);
}

export async function getActiveUser() {
  const activeId = hasStorage() ? window.localStorage.getItem(SESSION_KEY) : (await AsyncStorage.getItem(SESSION_KEY)) || memoryActiveStudentId;
  if (!activeId) return null;
  const users = await readUsers();
  return users.find((user) => user.studentId === activeId) || null;
}

export async function clearActiveUser() {
  memoryActiveStudentId = "";
  if (!hasStorage()) {
    await AsyncStorage.removeItem(SESSION_KEY);
    return;
  }
  window.localStorage.removeItem(SESSION_KEY);
}
