/** JSON contract for one browser session's household projection. */
export interface PlanVersion {
  title: string;
  date: string;
  time: string;
  person: string;
  preparation?: string;
  instructions?: string;
  location?: string;
  responsibility?: string;
  deadline?: string;
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
  preparation: string;
  instructions: string;
  location: string;
  responsibility: string;
  deadline: string;
  extraction: Record<string, {
    status: 'suggested' | 'conflicting' | 'invalid' | 'needs_date' | 'needs_context' | 'low_confidence' | 'ambiguous';
    evidence: {line: number; value: string; start?: number; end?: number}[];
    anchor?: string;
    confidence?: number;
    inferred?: boolean;
    candidate?: string;
  }>;
  interpretation?: {kind: string; kindConfidence: number; intent: string; intentConfidence: number};
}

export interface FollowThroughTask {
  id: string;
  title: string;
  plan: string;
  person: string;
  status: 'open' | 'done';
  due: string;
}

export interface Household {
  members: string[];
  sources: FamilySource[];
  plans: FamilyPlan[];
  tasks: FollowThroughTask[];
  createdSourceId?: string;
  access: {
    viewer: HouseholdAccess;
    people: HouseholdAccess[];
    invites: {id: string; name: string; expires: number}[];
  };
}

export interface HouseholdAccess {
  id: string;
  name: string;
  role: 'owner' | 'admin' | 'member';
}
