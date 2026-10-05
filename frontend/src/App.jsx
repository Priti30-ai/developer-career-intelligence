import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ModulePlaceholder from './pages/ModulePlaceholder';
import GitHubAnalysis from './pages/GitHubAnalysis';
import ResumeAnalysis from './pages/ResumeAnalysis';
import JobMatching from './pages/JobMatching';
import SkillGap from './pages/SkillGap';
import CareerRecommendations from './pages/CareerRecommendations';
import { APP_ROUTES, NAVIGATION_CONFIG } from './utils/constants';

// Find item config from centralized navigation configuration
const getItemConfig = (path) => {
  for (const group of NAVIGATION_CONFIG) {
    const item = group.items.find((i) => i.path === path);
    if (item) {
      return { ...item, group: group.group };
    }
  }
  return { name: 'Module', description: 'Module view', group: null, apiEndpoint: '' };
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          {/* Default and Dashboard Routes */}
          <Route path={APP_ROUTES.HOME} element={<Navigate to={APP_ROUTES.DASHBOARD} replace />} />
          <Route path={APP_ROUTES.DASHBOARD} element={<Dashboard />} />

          {/* Developer Analysis Routes */}
          <Route path={APP_ROUTES.GITHUB} element={<GitHubAnalysis />} />
          <Route
            path={APP_ROUTES.SKILLS}
            element={
              <ModulePlaceholder
                moduleName="Skill Profile"
                group="Developer Analysis"
                description={getItemConfig(APP_ROUTES.SKILLS).description}
                apiEndpoint={getItemConfig(APP_ROUTES.SKILLS).apiEndpoint}
                plannedCapabilities={[
                  'Validated core languages and framework proficiencies',
                  'Confidence scoring backed by code repository artifacts',
                  'Domain strengths across frontend, backend, databases, and DevOps',
                  'Dynamic profile evolution timeline'
                ]}
              />
            }
          />
          <Route path={APP_ROUTES.SKILL_GAPS} element={<SkillGap />} />
          <Route
            path={APP_ROUTES.REPOSITORY_ARCHITECTURE}
            element={
              <ModulePlaceholder
                moduleName="Repository Architecture"
                group="Developer Analysis"
                description={getItemConfig(APP_ROUTES.REPOSITORY_ARCHITECTURE).description}
                apiEndpoint={getItemConfig(APP_ROUTES.REPOSITORY_ARCHITECTURE).apiEndpoint}
                plannedCapabilities={[
                  'Directory depth, modularity, and layer separation metrics',
                  'Framework pattern detection (MVC, Clean Architecture, Microservices)',
                  'Code coupling, dependency tree depth, and cyclomatic complexity',
                  'Automated architectural health ratings'
                ]}
              />
            }
          />
          <Route
            path={APP_ROUTES.EVIDENCE}
            element={
              <ModulePlaceholder
                moduleName="Evidence & Artifacts"
                group="Developer Analysis"
                description={getItemConfig(APP_ROUTES.EVIDENCE).description}
                apiEndpoint={getItemConfig(APP_ROUTES.EVIDENCE).apiEndpoint}
                plannedCapabilities={[
                  'Cryptographic commit hash verification and authorship validation',
                  'Direct source code snippet provenance linking',
                  'Pull request diff verification and merge audit trails',
                  'Verification badges for verified technical resume claims'
                ]}
              />
            }
          />

          {/* Career Intelligence Routes */}
          <Route
            path={APP_ROUTES.CAREER_RECOMMENDATIONS}
            element={<CareerRecommendations />}
          />
          <Route path={APP_ROUTES.JOB_MATCHING} element={<JobMatching />} />
          <Route
            path={APP_ROUTES.LEARNING_ROADMAP}
            element={
              <ModulePlaceholder
                moduleName="Learning Roadmap"
                group="Career Intelligence"
                description={getItemConfig(APP_ROUTES.LEARNING_ROADMAP).description}
                apiEndpoint={getItemConfig(APP_ROUTES.LEARNING_ROADMAP).apiEndpoint}
                plannedCapabilities={[
                  'Step-by-step milestone curricula targeted to identified skill gaps',
                  'Curated documentation, textbooks, and repository projects',
                  'Estimated hours to competency based on learning curve models',
                  'Milestone completion checklists with progress persistence'
                ]}
              />
            }
          />

          {/* Documents Routes */}
          <Route path={APP_ROUTES.RESUME} element={<ResumeAnalysis />} />

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to={APP_ROUTES.DASHBOARD} replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
