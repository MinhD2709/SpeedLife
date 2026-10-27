import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

function runPython(payload) {
  return new Promise((resolve, reject) => {
    const python = process.env.PYTHON || path.join(root, '.venv', 'bin', 'python');
    const child = spawn(python, ['-m', 'app.engines.scout'], {
      cwd: path.join(root, 'backend'),
      env: { ...process.env, PYTHONPATH: path.join(root, 'backend') },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', code => {
      if (code !== 0) return reject(new Error(stderr || `Scout exited ${code}`));
      try { resolve(JSON.parse(stdout)); } catch (error) { reject(error); }
    });
    child.stdin.end(JSON.stringify(payload));
  });
}

export class Scout {
  constructor(options = {}) { this.options = options; }
  async decide(input) {
    const out = await runPython({ action: 'decide', options: this.options, input });
    const primary = out.intent?.primary;
    out.candidates = [
      { intent: primary, score: out.intent?.confidence ?? 0 },
      ...(out.intent?.alternates ?? [])
    ];
    out.toolPlan = (out.toolPlan ?? []).map(step => ({ ...step, capability: step.capability ?? step.tool }));
    if (out.executionContract?.intent && typeof out.executionContract.intent.primary === 'string') {
      out.executionContract.intent.primary = { id: out.executionContract.intent.primary };
    }
    return out;
  }
  classify(input) { return runPython({ action: 'classify', options: this.options, input }); }
}

export default { Scout };
