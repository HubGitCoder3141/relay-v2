/** JSON contract for one browser session's household projection. */
export interface PlanVersion {
  title: string;
  date: string;
  time: string;
  person: string;
  sourceId: string;
}

export interface FamilyPlan extends PlanVersion {
  id: string;
  history: PlanVersion[];
}

export interface FamilySource {
  id: string;
  title: string;
  text: string;
  status: 'pending' | 'approved' | 'rejected';
  date: string;
  time: string;
  person: string;
  target: string | null;
}

export interface FollowThroughTask {
  id: string;
  title: string;
  plan: string;
  person: string;
  status: 'open' | 'done';
}

export interface Household {
  members: string[];
  sources: FamilySource[];
  plans: FamilyPlan[];
  tasks: FollowThroughTask[];
}
