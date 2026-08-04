"use client";

import { useEffect, useState } from "react";
import { createUser } from "@/lib/api";

const STORAGE_KEY = "payment-copilot:userId";

export function useCurrentUser() {
  const [userId, setUserId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setUserId(Number(stored));
      return;
    }
    createUser("guest")
      .then((user) => {
        window.localStorage.setItem(STORAGE_KEY, String(user.id));
        setUserId(user.id);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  return { userId, error };
}
