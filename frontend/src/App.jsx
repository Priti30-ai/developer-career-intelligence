import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ModulePlaceholder from './pages/ModulePlaceholder';
import GitHubAnalysis from './pages/GitHubAnalysis';
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
          <Route
            path={APP_ROUTES.SKILL_GAPS}
            element={
              <ModulePlaceholder
                moduleName="Skill Gaps"
                group="Developer Analysis"
                description={getItemConfig(APP_ROUTES.SKILL_GAPS).description}
                apiEndpoint={getItemConfig(APP_ROUTES.SKILL_GAPS).apiEndpoint}
                plannedCapabilities={[
                  'Comparative delta against target role benchmarks',
                  'Categorization of missing, nascent, and proficient competencies',
                  'Weighting of essential vs nice-to-have technical skills',
                  'Impact score estimation for closing specific gaps'
                ]}
              />
            }
          />
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
            element={
              <ModulePlaceholder
                moduleName="Career Recommendations"
                group="Career Intelligence"
                description={getItemConfig(APP_ROUTES.CAREER_RECOMMENDATIONS).description}
                apiEndpoint={getItemConfig(APP_ROUTES.CAREER_RECOMMENDATIONS).apiEndpoint}
                plannedCapabilities={[
                  'Algorithmic suitability scoring for adjacent engineering roles',
                  'Trajectory progression modeling (Junior -> Mid -> Senior -> Staff)',
                  'Market demand alignment and compensation bracket indicators',
                  'Actionable prerequisites for career pivots'
                ]}
              />
            }
          />
          <Route
            path={APP_ROUTES.JOB_MATCHING}
            element={
              <ModulePlaceholder
                moduleName="Job Matching"
                group="Career Intelligence"
                description={getItemConfig(APP_ROUTES.JOB_MATCHING).description}
                apiEndpoint={getItemConfig(APP_ROUTES.JOB_MATCHING).apiEndpoint}
                plannedCapabilities={[
                  'Semantic embedding similarity against verified job postings',
                  'Threshold matching breakdown (experience, stack, seniority)',
                  'Custom filter controls by location, remote policy, and role type',
                  'Match confidence breakdown with grounded justification'
                ]}
              />
            }
          />
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
          <Route
            path={APP_ROUTES.RESUME}
            element={
              <ModulePlaceholder
                moduleName="Resume Analysis"
                group="Documents"
                description={getItemConfig(APP_ROUTES.RESUME).description}
                apiEndpoint={getItemConfig(APP_ROUTES.RESUME).apiEndpoint}
                plannedCapabilities={[
                  'PDF / DOCX document parsing and section classification',
                  'Claim extraction and semantic entity tagging',
                  'Cross-referencing claims against GitHub repository evidence',
                  'Discrepancy detection and claim verification scorecard'
                ]}
              />
            }
          />

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to={APP_ROUTES.DASHBOARD} replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
