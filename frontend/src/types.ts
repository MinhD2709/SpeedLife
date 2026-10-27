export type UnitStatus = 'completed' | 'current' | 'credited' | 'failed' | 'unknown';

export type StudentUnit = {
  code: string;
  status: UnitStatus;
  mark: number | null;
  credit_points: number;
  source_document?: string | null;
  page?: number | null;
};

export type StudentRecord = {
  degree: string;
  major: string;
  handbook_year: number;
  units: StudentUnit[];
};

export type ExtractionResponse = {
  record: StudentRecord;
  documents: { filename: string; pages: number; units_found: number }[];
  warnings: string[];
  confirmation_required: boolean;
};

export type PlanUnit = {
  code: string;
  title: string;
  credit_points: number;
  requirement_group: string;
  reason: string;
  source_url: string;
};

export type PlanResponse = {
  status: 'complete' | 'clarification';
  clarification?: { question: string; options: string[] } | null;
  next_term: PlanUnit[];
  excluded: { code: string; title: string; reason: string }[];
  outlook: { session: string; units: string[]; note: string }[];
  narrative: string;
  evidence: { label: string; url: string }[];
  trace: string[];
  contract_id?: string | null;
  intent?: string | null;
};

export type IntegrationStatus = {
  mode: string;
  zetaris: { state: string; error?: string };
  meterless: { state: string; model?: string; error?: string };
  scout: { state: string; registry_version: number; engine: string };
  live_ready: boolean;
};
