/* eslint-disable @typescript-eslint/ban-ts-comment */
// Plain JavaScript version of changelog generator so we don't rely on ts-node.
const fs = require('fs');
const path = require('path');

/** @typedef {{ sha: string, date: string, message: string }} Commit */

const GIT_LOG_PATH = path.resolve(__dirname, '..', 'git_log.txt');
const OUTPUT_PATH = path.resolve(__dirname, '..', 'frontend', 'src', 'lib', 'generated', 'changelog_data.ts');

const THEME_DEFS = [
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

/**
 * @returns {Commit[]}
 */
function readGitLog() {
    const raw = fs.readFileSync(GIT_LOG_PATH, 'utf-8');
    const lines = raw.split(/\r?\n/);
    const commits = [];
    let i = 0;
    while (i < lines.length) {
        const line = lines[i];
        if (line.startsWith('COMMIT: ')) {
            const sha = line.substring(8).trim();
            const dateLine = lines[++i] || '';
            const dateMatch = dateLine.match(/DATE:(\d{4}-\d{2}-\d{2})/);
            const date = dateMatch ? dateMatch[1] : 'unknown';
            while (i < lines.length && !lines[i].startsWith('MESSAGE:')) i++;
            i++;
            const msgLines = [];
            while (i < lines.length && !lines[i].startsWith('COMMIT: ')) {
                msgLines.push(lines[i]);
                i++;
            }
            const messageFull = msgLines.join(' ').trim();
            const firstSentence = messageFull.split(/[\.\n\r]/)[0].replace(/^[-\s]*/, '').trim();
            commits.push({ sha, date, message: firstSentence });
        } else {
            i++;
        }
    }
    return commits;
}

function classifyTheme(message) {
    const lower = message.toLowerCase();
    for (const def of THEME_DEFS) {
        if (def.keywords.some((k) => lower.includes(k))) return { id: def.id, title: def.title };
    }
    return { id: 'misc', title: 'Miscellaneous' };
}

function buildChangelog(commits) {
    /** @type {Map<string, any>} */
    const monthMap = new Map();
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    for (const c of commits) {
        const [year, monthStr] = c.date.split('-');
        const monthIdx = parseInt(monthStr, 10) - 1;
        const monthName = monthNames[monthIdx] || 'Unknown';
        const monthId = `${monthName.toLowerCase()}-${year}`;
        const monthTitle = `${monthName} ${year}`;
        if (!monthMap.has(monthId)) monthMap.set(monthId, { id: monthId, title: monthTitle, themes: [] });
        const monthObj = monthMap.get(monthId);
        const themeInfo = classifyTheme(c.message);
        let themeObj = monthObj.themes.find((t) => t.id === themeInfo.id);
        if (!themeObj) {
            themeObj = { id: themeInfo.id, title: themeInfo.title, entries: [] };
            monthObj.themes.push(themeObj);
        }
        themeObj.entries.push({ date: c.date, text: c.message, sha: c.sha });
    }

    const monthsSorted = Array.from(monthMap.values()).sort((a, b) => (a.title < b.title ? 1 : -1));
    for (const m of monthsSorted) {
        m.themes.sort((a, b) => a.title.localeCompare(b.title));
        for (const t of m.themes) t.entries.sort((a, b) => (a.date < b.date ? 1 : -1));
    }
    return monthsSorted;
}

function emitFile(changelog) {
    const header = `// AUTO-GENERATED. Do not edit directly.\n` +
        `// Regenerate via: npm run generate:changelog\n\n` +
        `export interface ChangelogEntry { date: string; text: string; sha: string; }\n` +
        `export interface ChangelogTheme { id: string; title: string; entries: ChangelogEntry[]; }\n` +
        `export interface ChangelogMonth { id: string; title: string; themes: ChangelogTheme[]; }\n` +
        `export const changelog: ChangelogMonth[] = `;
    const content = JSON.stringify(changelog, null, 2);
    fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
    fs.writeFileSync(OUTPUT_PATH, header + content + ';\n', 'utf-8');
    console.log(`Generated changelog with ${changelog.reduce((s, m) => s + m.themes.reduce((a, t) => a + t.entries.length, 0), 0)} entries.`);
}

function main() {
    const commits = readGitLog();
    const changelog = buildChangelog(commits);
    emitFile(changelog);
}

main(); 