/**
 * Application constants and centralized navigation/route configuration
 */

export const APP_NAME = 'Developer Career Intelligence System';
export const APP_VERSION = '1.0.0';

// Frontend Application Routes
export const APP_ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  GITHUB: '/github',
  SKILLS: '/skills',
  SKILL_GAPS: '/skill-gaps',
  REPOSITORY_ARCHITECTURE: '/repository-architecture',
  EVIDENCE: '/evidence',
  CAREER_RECOMMENDATIONS: '/career-recommendations',
  JOB_MATCHING: '/job-matching',
  LEARNING_ROADMAP: '/learning-roadmap',
  RESUME: '/resume',
};

// Backend API Endpoints (relative to VITE_API_BASE_URL)
export const API_ROUTES = {
  HEALTH: '/health',
  DEVELOPER_PROFILE: '/developer-profile',
  SKILL_GAP: '/skill-gap',
  RESUME: '/resume',
  EVIDENCE: '/evidence',
  JOB_MATCHING: '/job-matching',
  CAREER_RECOMMENDATIONS: '/career-recommendations',
  REPOSITORY_ARCHITECTURE: '/repository-architecture',
};

// Navigation Structure organized by functional domains
export const NAVIGATION_CONFIG = [
  {
    group: null, // Top-level
    items: [
      {
        name: 'Dashboard',
        path: APP_ROUTES.DASHBOARD,
        icon: 'LayoutDashboard',
        description: 'System overview, backend health, and pipeline integration roadmap.',
        status: 'active',
      },
    ],
  },
  {
    group: 'Developer Analysis',
    items: [
      {
        name: 'GitHub Analysis',
        path: APP_ROUTES.GITHUB,
        icon: 'GitBranch',
        description: 'Repository commit histories, code velocity, language distribution, and pull request activity.',
        apiEndpoint: '/api/github/{username}',
        status: 'active',
      },
      {
        name: 'Skill Profile',
        path: APP_ROUTES.SKILLS,
        icon: 'Cpu',
        description: 'Normalized technical competencies, framework proficiencies, and experience weights extracted from verified sources.',
        apiEndpoint: '/api/v1/developer-profile',
        status: 'in-progress',
      },
      {
        name: 'Skill Gaps',
        path: APP_ROUTES.SKILL_GAPS,
        icon: 'Target',
        description: 'Comparative gap calculations between candidate skill sets and target role benchmarks.',
        apiEndpoint: '/api/v1/skill-gap/analyze',
        status: 'active',
      },
      {
        name: 'Repository Architecture',
        path: APP_ROUTES.REPOSITORY_ARCHITECTURE,
        icon: 'Network',
        description: 'Structural pattern detection, module modularity, and layered architectural analysis of developer repositories.',
        apiEndpoint: '/api/v1/repository-architecture',
        status: 'in-progress',
      },
      {
        name: 'Evidence',
        path: APP_ROUTES.EVIDENCE,
        icon: 'ShieldCheck',
        description: 'Cryptographic commit verifications, artifact provenance records, and grounded claim validations.',
        apiEndpoint: '/api/v1/evidence',
        status: 'in-progress',
      },
    ],
  },
  {
    group: 'Career Intelligence',
    items: [
      {
        name: 'Career Recommendations',
        path: APP_ROUTES.CAREER_RECOMMENDATIONS,
        icon: 'Compass',
        description: 'Algorithmic career progression options, role transitions, and trajectory modeling based on verified evidence.',
        apiEndpoint: '/api/v1/career-recommendations/analyze',
        status: 'active',
      },
      {
        name: 'Job Matching',
        path: APP_ROUTES.JOB_MATCHING,
        icon: 'Briefcase',
        description: 'Deterministic skill matching and gap coverage analysis against job description requirements.',
        apiEndpoint: '/api/v1/job-matching/analyze',
        status: 'active',
      },
      {
        name: 'Learning Roadmap',
        path: APP_ROUTES.LEARNING_ROADMAP,
        icon: 'GraduationCap',
        description: 'Prioritized learning curricula, targeted documentation milestones, and actionable upskilling steps.',
        apiEndpoint: '/api/v1/career-recommendations',
        status: 'in-progress',
      },
    ],
  },
  {
    group: 'Documents',
    items: [
      {
        name: 'Resume Analysis',
        path: APP_ROUTES.RESUME,
        icon: 'FileText',
        description: 'Document extraction (PDF/DOCX/TXT), normalized skill identification, and structured career timeline alignment.',
        apiEndpoint: '/api/v1/resume/analyze',
        status: 'active',
      },
    ],
  },
];

// Helper to look up route metadata by path
export const getRouteMetadata = (pathname) => {
  for (const section of NAVIGATION_CONFIG) {
    const match = section.items.find((item) => item.path === pathname);
    if (match) {
      return {
        ...match,
        group: section.group,
      };
    }
  }
  // Default to Dashboard metadata if not matched
  return {
    name: 'Dashboard',
    path: APP_ROUTES.DASHBOARD,
    group: null,
    description: 'System overview and pipeline status.',
  };
};
