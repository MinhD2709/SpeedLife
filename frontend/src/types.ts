export type Citation = { source_id: string; filename: string; page: number; text: string };
export type CheatSheet = {
  mode: string;
  title: string;
  points: { text: string; citation: Citation }[];
  warnings: string[];
  trace: string[];
};
