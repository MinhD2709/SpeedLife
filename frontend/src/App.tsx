import { useMemo, useState } from 'react';

type Country = 'Any' | 'United States' | 'United Kingdom' | 'Canada' | 'Australia' | 'Europe';
type Degree = 'Undergraduate' | "Master's" | 'PhD';
type Budget = 'Scholarship first' | 'Balanced' | 'Flexible';
type StudyArea = 'Computer Science' | 'Business' | 'Engineering' | 'Health Sciences' | 'Design';
type Pace = 'Balanced' | 'Accelerated';
type DegreeLength = '2 years' | '2.5 years' | '3 years' | '3.5+ years';

type University = {
  name: string;
  country: Country;
  degree: Degree;
  area: StudyArea;
  tuition: string;
  deadline: string;
  acceptance: string;
  scholarship: string;
  highlight: string;
  reason: string;
  sourceLabel: string;
  sourceUrl: string;
  officialData: {
    durationYears: number;
    standardLoad: number;
    maxLoad: number;
    notes: string;
  };
};

const universityCatalog: University[] = [
  {
    name: 'UNSW Sydney',
    country: 'Australia',
    degree: 'Undergraduate',
    area: 'Computer Science',
    tuition: '$42K / year',
    deadline: 'Nov 30',
    acceptance: '65% avg',
    scholarship: 'Merit and equity scholarships',
    highlight: 'Strong software engineering and AI programs',
    reason: 'A good fit if you want a strong tech reputation in Australia with practical career outcomes.',
    sourceLabel: 'UNSW handbook',
    sourceUrl: 'https://www.handbook.unsw.edu.au/',
    officialData: {
      durationYears: 3,
      standardLoad: 4,
      maxLoad: 5,
      notes: 'Typical full-time study is 4 courses per semester, with overloads allowed subject to approval.'
    }
  },
  {
    name: 'University of Sydney',
    country: 'Australia',
    degree: 'Undergraduate',
    area: 'Computer Science',
    tuition: '$46K / year',
    deadline: 'Dec 31',
    acceptance: '66% avg',
    scholarship: 'International scholarships',
    highlight: 'Research and analytics strength',
    reason: 'Great for students who want a highly regarded program and strong global alumni connections.',
    sourceLabel: 'University of Sydney study pages',
    sourceUrl: 'https://www.sydney.edu.au/courses/',
    officialData: {
      durationYears: 3,
      standardLoad: 4,
      maxLoad: 5,
      notes: 'Normal full-time progress is based on a fixed credit load per semester and is published in the course handbook.'
    }
  },
  {
    name: 'University of Toronto',
    country: 'Canada',
    degree: "Master's",
    area: 'Computer Science',
    tuition: '$32K / year',
    deadline: 'Jan 15',
    acceptance: '24%',
    scholarship: 'Graduate funding available',
    highlight: 'AI, ML, and data science leadership',
    reason: 'Very strong value and research reputation for computer science applicants.',
    sourceLabel: 'U of T School of Graduate Studies',
    sourceUrl: 'https://www.sgs.utoronto.ca/',
    officialData: {
      durationYears: 2,
      standardLoad: 2,
      maxLoad: 3,
      notes: 'Full-time master\'s programs usually follow a normal course-per-term structure published by the faculty.'
    }
  },
  {
    name: 'University of Edinburgh',
    country: 'United Kingdom',
    degree: "Master's",
    area: 'Computer Science',
    tuition: '$36K / year',
    deadline: 'Jan 31',
    acceptance: '28%',
    scholarship: 'Merit scholarships',
    highlight: 'AI and machine learning research',
    reason: 'A solid choice for students pursuing research and applied AI work in Europe.',
    sourceLabel: 'University of Edinburgh course info',
    sourceUrl: 'https://www.ed.ac.uk/studying',
    officialData: {
      durationYears: 1,
      standardLoad: 2,
      maxLoad: 3,
      notes: 'Master\'s study load depends on the program pattern published by the school and is normally set by course selection.'
    }
  },
  {
    name: 'University of British Columbia',
    country: 'Canada',
    degree: 'Undergraduate',
    area: 'Engineering',
    tuition: '$28K / year',
    deadline: 'Jan 15',
    acceptance: '38%',
    scholarship: 'Need and merit awards',
    highlight: 'Research-heavy engineering culture',
    reason: 'Excellent if you want strong engineering credibility and a manageable cost base.',
    sourceLabel: 'UBC admissions and programs',
    sourceUrl: 'https://engineering.ubc.ca/',
    officialData: {
      durationYears: 4,
      standardLoad: 5,
      maxLoad: 6,
      notes: 'The standard undergraduate load is usually fixed by the faculty and may be adjusted with approval.'
    }
  },
  {
    name: 'Imperial College London',
    country: 'United Kingdom',
    degree: 'Undergraduate',
    area: 'Engineering',
    tuition: '$42K / year',
    deadline: 'Jan 31',
    acceptance: '15%',
    scholarship: 'Excellence awards',
    highlight: 'Highly selective STEM brand',
    reason: 'Best for applicants with a very strong academic profile and a clear engineering direction.',
    sourceLabel: 'Imperial undergraduate programs',
    sourceUrl: 'https://www.imperial.ac.uk/study/',
    officialData: {
      durationYears: 3,
      standardLoad: 4,
      maxLoad: 5,
      notes: 'Engineering study pace is defined by the department handbook and course structure.'
    }
  }
];

const defaultProfile = {
  country: 'Any' as Country,
  degree: "Master's" as Degree,
  area: 'Computer Science' as StudyArea,
  budget: 'Balanced' as Budget,
  pace: 'Balanced' as Pace,
  preferredLength: '2.5 years' as DegreeLength,
  gpa: '3.7',
  goal: 'Build AI products and join a research-intensive program.'
};

function parseTuition(value: string): number {
  const cleaned = value.replace(/[$,\s/]+/g, '').replace(/year|yr/gi, '').replace(/\./g, '');
  const numeric = Number.parseFloat(cleaned);
  return Number.isFinite(numeric) ? numeric : 0;
}

function getRecommendations(profile: typeof defaultProfile) {
  const gpa = Number(profile.gpa);
  const goalLower = profile.goal.toLowerCase();

  const scored = universityCatalog
    .filter((school) => profile.country === 'Any' || school.country === profile.country)
    .filter((school) => school.degree === profile.degree && school.area === profile.area)
    .map((school) => {
      let score = 60;
      const reasons: string[] = [];

      if (gpa >= 3.8) score += 18;
      else if (gpa >= 3.5) score += 10;
      else score -= 6;

      if (profile.budget === 'Scholarship first' && /scholarship|aid|funding/i.test(school.scholarship)) {
        score += 16;
        reasons.push('Scholarships are a good fit for your budget strategy');
      } else if (profile.budget === 'Balanced') {
        score += 6;
      }

      if (goalLower.includes('ai') && /ai|ml|data|research/i.test(school.highlight)) {
        score += 12;
        reasons.push('Strong fit with your AI and research interest');
      }

      if (profile.pace === 'Accelerated') {
        const overload = school.officialData.maxLoad - school.officialData.standardLoad;
        if (overload > 0) {
          score += 8;
          reasons.push(`Potential accelerated load: ${school.officialData.maxLoad} vs ${school.officialData.standardLoad} per term`);
        }
      }

      if (profile.preferredLength === '2 years' && school.officialData.durationYears <= 2) score += 10;
      if (profile.preferredLength === '2.5 years' && school.officialData.durationYears <= 3) score += 8;
      if (profile.preferredLength === '3 years' && school.officialData.durationYears === 3) score += 8;
      if (profile.preferredLength === '3.5+ years' && school.officialData.durationYears >= 3) score += 7;

      const tuitionCost = parseTuition(school.tuition);
      if (profile.budget === 'Flexible') {
        score += 4;
      } else if (profile.budget === 'Scholarship first' && tuitionCost < 30000) {
        score += 6;
      }

      score = Math.max(52, Math.min(score, 97));

      const advice = buildAdvice(school, profile);
      reasons.push(advice);

      return { ...school, score, reasons };
    })
    .sort((a, b) => b.score - a.score);

  return scored.length ? scored : universityCatalog.slice(0, 3).map((school) => ({
    ...school,
    score: 68,
    reasons: ['This is a broad recommendation and should be checked against the university handbook before making a final decision.']
  }));
}

function buildAdvice(school: University, profile: typeof defaultProfile) {
  const overload = school.officialData.maxLoad - school.officialData.standardLoad;

  if (profile.pace === 'Accelerated' && overload > 0) {
    return `You may be able to shorten the timeline by taking ${school.officialData.maxLoad} units per semester instead of the standard ${school.officialData.standardLoad}, but the university must approve the overload.`;
  }

  if (profile.preferredLength === '2.5 years') {
    return `This program is usually completed in about ${school.officialData.durationYears} years at the standard pace. A faster completion path depends on approved overloads and course availability.`;
  }

  return `The published study pattern suggests a standard ${school.officialData.durationYears}-year route, but the final timeline should be checked against the official study handbook.`;
}

function buildApplicationPlan(topMatch: ReturnType<typeof getRecommendations>[number]) {
  return [
    {
      label: 'Verify program rules',
      detail: `Check the official ${topMatch.sourceLabel.toLowerCase()} and confirm the published study pattern, timeline, and course load for ${topMatch.name}.`
    },
    {
      label: 'Budget planning',
      detail: `Review tuition, living costs, and scholarship requirements for ${topMatch.name} before confirming any final shortlist.`
    },
    {
      label: 'Prepare evidence',
      detail: 'Collect transcripts, GPA evidence, extracurriculars, and any work samples or research experience that match your chosen field.'
    },
    {
      label: 'Submit early',
      detail: `Track the ${topMatch.deadline} application deadline and build the final statement of purpose around the school’s alignment with your goals.`
    }
  ];
}

export default function App() {
  const [profile, setProfile] = useState(defaultProfile);
  const recommendations = useMemo(() => getRecommendations(profile), [profile]);
  const topMatch = recommendations[0];
  const applicationPlan = topMatch ? buildApplicationPlan(topMatch) : [];

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">UniPilot AI</p>
          <h1>University matching with verified program rules.</h1>
          <p className="lead">
            The agent asks for your budget, preferred duration, study area, and pace, then compares options against official university study patterns.
          </p>
          <div className="pill-row">
            <span>Official-source matching</span>
            <span>Tuition & deadline tracking</span>
            <span>Degree-speed guidance</span>
          </div>
        </div>

        <div className="insight-box">
          <p className="mini-label">AI recommendation</p>
          <h2>{topMatch ? topMatch.name : 'Create your profile'}</h2>
          <p>{topMatch ? `${topMatch.score}% match` : 'Your best-fit universities will appear here.'}</p>
          <ul>
            {topMatch
              ? topMatch.reasons.slice(0, 3).map((reason) => <li key={reason}>{reason}</li>)
              : <li>Answer a few questions to compare study plans and university fit.</li>}
          </ul>
        </div>
      </section>

      <section className="panel-grid">
        <form className="control-panel" onSubmit={(event) => event.preventDefault()}>
          <h3>Tell the agent about you</h3>

          <label>
            Country
            <select value={profile.country} onChange={(event) => setProfile({ ...profile, country: event.target.value as Country })}>
              <option value="Any">Any</option>
              <option value="United States">United States</option>
              <option value="United Kingdom">United Kingdom</option>
              <option value="Canada">Canada</option>
              <option value="Australia">Australia</option>
              <option value="Europe">Europe</option>
            </select>
          </label>

          <label>
            Degree level
            <select value={profile.degree} onChange={(event) => setProfile({ ...profile, degree: event.target.value as Degree })}>
              <option value="Undergraduate">Undergraduate</option>
              <option value="Master's">Master's</option>
              <option value="PhD">PhD</option>
            </select>
          </label>

          <label>
            Study area
            <select value={profile.area} onChange={(event) => setProfile({ ...profile, area: event.target.value as StudyArea })}>
              <option value="Computer Science">Computer Science</option>
              <option value="Business">Business</option>
              <option value="Engineering">Engineering</option>
              <option value="Health Sciences">Health Sciences</option>
              <option value="Design">Design</option>
            </select>
          </label>

          <label>
            Budget strategy
            <select value={profile.budget} onChange={(event) => setProfile({ ...profile, budget: event.target.value as Budget })}>
              <option value="Scholarship first">Scholarship first</option>
              <option value="Balanced">Balanced</option>
              <option value="Flexible">Flexible</option>
            </select>
          </label>

          <label>
            Preferred pace
            <select value={profile.pace} onChange={(event) => setProfile({ ...profile, pace: event.target.value as Pace })}>
              <option value="Balanced">Balanced</option>
              <option value="Accelerated">Accelerated</option>
            </select>
          </label>

          <label>
            Desired duration
            <select value={profile.preferredLength} onChange={(event) => setProfile({ ...profile, preferredLength: event.target.value as DegreeLength })}>
              <option value="2 years">2 years</option>
              <option value="2.5 years">2.5 years</option>
              <option value="3 years">3 years</option>
              <option value="3.5+ years">3.5+ years</option>
            </select>
          </label>

          <label>
            GPA / predicted grades
            <input
              type="number"
              min="1"
              max="4"
              step="0.1"
              value={profile.gpa}
              onChange={(event) => setProfile({ ...profile, gpa: event.target.value })}
            />
          </label>

          <label>
            Career goal
            <textarea
              value={profile.goal}
              onChange={(event) => setProfile({ ...profile, goal: event.target.value })}
              rows={3}
            />
          </label>
        </form>

        <div className="results-panel">
          <div className="section-header">
            <h3>Shortlist</h3>
            <span>{recommendations.length} matched universities</span>
          </div>

          {recommendations.map((school) => (
            <article key={school.name} className="school-card">
              <div className="school-header">
                <div>
                  <h4>{school.name}</h4>
                  <p>{school.country} • {school.degree}</p>
                </div>
                <div className="score-pill">{school.score}%</div>
              </div>

              <div className="meta-grid">
                <span>{school.area}</span>
                <span>{school.tuition}</span>
                <span>Deadline: {school.deadline}</span>
                <span>Acceptance: {school.acceptance}</span>
              </div>

              <p className="highlight">{school.highlight}</p>
              <p className="reason">{school.reason}</p>

              <div className="source-box">
                <strong>Official source:</strong>{' '}
                <a href={school.sourceUrl} target="_blank" rel="noreferrer">{school.sourceLabel}</a>
              </div>

              <div className="study-note">
                <strong>Study pattern:</strong> {school.officialData.notes}
              </div>

              <ul>
                {school.reasons.map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="application-panel">
        <div>
          <p className="mini-label">Application coach</p>
          <h3>Suggested action plan</h3>
        </div>

        <div className="plan-grid">
          {applicationPlan.map((step) => (
            <div key={step.label} className="plan-item">
              <span>{step.label}</span>
              <p>{step.detail}</p>
            </div>
          ))}
        </div>

        <p className="verification-note">
          Important: degree durations and course loads should be checked against the official university course handbook before finalising an application. The agent should treat university websites as the source of truth and cite those pages when giving advice.
        </p>
      </section>
    </main>
  );
}
