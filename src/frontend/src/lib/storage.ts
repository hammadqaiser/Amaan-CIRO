import { openDB } from 'idb';
import type { DBSchema, IDBPDatabase } from 'idb';

interface Alert {
  id: string;
  audience: string;
  channel: string;
  language: string;
  subject: string;
  body: string;
  urgency_level: string;
  sent_at: string; // ISO timestamp
}

interface CiroDB extends DBSchema {
  alerts: {
    key: string;
    value: Alert;
    indexes: { 'by-date': string };
  };
}

let dbPromise: Promise<IDBPDatabase<CiroDB>> | null = null;

export const initDB = () => {
  if (!dbPromise) {
    dbPromise = openDB<CiroDB>('ciro-alerts-db', 1, {
      upgrade(db) {
        const store = db.createObjectStore('alerts', {
          keyPath: 'id',
        });
        store.createIndex('by-date', 'sent_at');
      },
    });
  }
  return dbPromise;
};

export const saveAlerts = async (alerts: Alert[]) => {
  const db = await initDB();
  const tx = db.transaction('alerts', 'readwrite');
  
  // Prune alerts older than 5 days
  const fiveDaysAgo = new Date();
  fiveDaysAgo.setDate(fiveDaysAgo.getDate() - 5);
  const cutoffDate = fiveDaysAgo.toISOString();

  const allAlerts = await tx.store.index('by-date').getAll();
  for (const alert of allAlerts) {
    if (alert.sent_at < cutoffDate) {
      tx.store.delete(alert.id);
    }
  }

  // Save new alerts
  for (const alert of alerts) {
    tx.store.put(alert);
  }
  await tx.done;
};

export const getAlerts = async (): Promise<Alert[]> => {
  const db = await initDB();
  // Get all alerts sorted by date, then reverse to get newest first
  const alerts = await db.getAllFromIndex('alerts', 'by-date');
  return alerts.reverse();
};
