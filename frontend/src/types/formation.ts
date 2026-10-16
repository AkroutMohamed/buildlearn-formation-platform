export interface Formation {
  id: string;
  title: string;
  description: string;
  thumbnail: string | null;
  category: string;
  level: string;
  language: string;
  duration: number;
  instructor: string;
}

export interface FormationPage {
  items: Formation[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
}
