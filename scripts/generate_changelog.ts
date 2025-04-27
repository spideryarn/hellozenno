// @ts-nocheck
import fs from 'fs';
import path from 'path';

interface Commit {
  sha: string;
  date: string; // YYYY-MM-DD
  message: string;
}

interface ChangelogEntry { date: string; text: string; sha: string; }
interface ChangelogTheme { id: string; title: string; entries: ChangelogEntry[]; }
interface ChangelogMonth { id: string; title: string; themes: ChangelogTheme[]; }

const GIT_LOG_PATH = path.resolve(__dirname, '..', 'git_log.txt');
const OUTPUT_PATH = path.resolve(__dirname, '..', 'frontend', 'src', 'lib', 'generated', 'changelog_data.ts');

const THEME_DEFS: { id: string; title: string; keywords: string[] }[] = [
  { id: 'ui-components', title: 'UI & Components', keywords: ['datagrid', 'component', 'css', 'tooltip', 'style', 'ui', 'svelte'] },
  { id: 'profile-user', title: 'Profile & User', keywords: ['profile', 'user'] },
  { id: 'seo-analytics', title: 'SEO & Analytics', keywords: ['sitemap', 'seo', 'analytics', 'privacy', 'terms', 'robots'] },
  { id: 'auth-security', title: 'Auth & Security', keywords: ['auth', 'authentication', 'supabase', 'jwt', 'login', 'signup'] },
  { id: 'backend-database', title: 'Backend & Database', keywords: ['database', 'migration', 'api', 'backend', 'model', 'peewee', 'postgres'] },
  { id: 'flashcards-content', title: 'Flashcards & Content', keywords: ['flashcard', 'translation', 'sentence', 'phrase', 'wordform', 'lemma'] },
  { id: 'deployment-ops', title: 'Deployment & Ops', keywords: ['deploy', 'vercel', 'docker', 'ci', 'script'] },
  { id: 'docs-testing', title: 'Documentation & Testing', keywords: ['docs', 'readme', 'test', 'pytest', 'playwright', 'story'] },
  { id: 'misc', title: 'Miscellaneous', keywords: [] }
];

function readGitLog(): Commit[] {
  const raw = fs.readFileSync(GIT_LOG_PATH, 'utf-8');
  const lines = raw.split(/\r?\n/);
  const commits: Commit[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith('COMMIT: ')) {
      const sha = line.substring(8).trim();
      const dateLine = lines[++i] || '';
      const dateMatch = dateLine.match(/DATE:(\d{4}-\d{2}-\d{2})/);
      const date = dateMatch ? dateMatch[1] : 'unknown';
      // Skip to MESSAGE line
      while (i < lines.length && !lines[i].startsWith('MESSAGE:')) i++;
      i++; // move to first message line
      const messageLines: string[] = [];
      while (i < lines.length && !lines[i].startsWith('COMMIT: ')) {
        messageLines.push(lines[i]);
        i++;
      }
      const messageFull = messageLines.join(' ').trim();
      const messageFirstSentence = messageFull.split(/\. |\n|\r/)[0].replace(/^-\s*/, '').trim();
      commits.push({ sha, date, message: messageFirstSentence });
    } else {
      i++;
    }
  }
  return commits;
}

function classifyTheme(msg: string): { id: string; title: string } {
  const lower = msg.toLowerCase();
  for (const def of THEME_DEFS) {
    if (def.keywords.some(k => lower.includes(k))) {
      return { id: def.id, title: def.title };
    }
  }
  return { id: 'misc', title: 'Miscellaneous' };
}

function buildChangelog(commits: Commit[]): ChangelogMonth[] {
  const monthMap = new Map<string, ChangelogMonth>();
  const monthNames = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ];

  for (const commit of commits) {
    const [year, monthNum] = commit.date.split('-');
    const monthIdx = parseInt(monthNum, 10) - 1;
    const monthName = monthNames[monthIdx];
    const monthId = `${monthName.toLowerCase()}-${year}`;
    const monthTitle = `${monthName} ${year}`;

    if (!monthMap.has(monthId)) {
      monthMap.set(monthId, { id: monthId, title: monthTitle, themes: [] });
    }
    const monthObj = monthMap.get(monthId)!;

    const themeInfo = classifyTheme(commit.message);
    let themeObj = monthObj.themes.find(t => t.id === themeInfo.id);
    if (!themeObj) {
      themeObj = { id: themeInfo.id, title: themeInfo.title, entries: [] };
      monthObj.themes.push(themeObj);
    }

    themeObj.entries.push({ date: commit.date, text: commit.message, sha: commit.sha });
  }

  // Sort themes and months chronologically descending
  const monthsSorted = Array.from(monthMap.values()).sort((a,b) => (a.title < b.title ? 1 : -1));
  for (const m of monthsSorted) {
    m.themes.sort((a,b) => a.title.localeCompare(b.title));
    for (const t of m.themes) {
      t.entries.sort((a,b) => (a.date < b.date ? 1 : -1));
    }
  }
  return monthsSorted;
}

function emitFile(changelog: ChangelogMonth[]) {
  const header = `// AUTO-GENERATED. Do not edit directly.\n`+
    `// Regenerate via: npm run generate:changelog\n\n`+
    `export interface ChangelogEntry { date: string; text: string; sha: string; }\n`+
    `export interface ChangelogTheme { id: string; title: string; entries: ChangelogEntry[]; }\n`+
    `export interface ChangelogMonth { id: string; title: string; themes: ChangelogTheme[]; }\n`+
    `export const changelog: ChangelogMonth[] = `;

  const content = JSON.stringify(changelog, null, 2);
  const fileContent = header + content + ';\n';

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, fileContent, 'utf-8');
  console.log(`Generated changelog with ${changelog.reduce((sum,m)=>sum+m.themes.reduce((s,t)=>s+t.entries.length,0),0)} entries.`);
}

function main() {
  const commits = readGitLog();
  const changelog = buildChangelog(commits);
  emitFile(changelog);
}

main(); 