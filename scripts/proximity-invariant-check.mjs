// Proximity monitoring is derived state: it is only correct if EVERY place that
// changes the set of active calls, and every place the audio route can change,
// re-derives it. The failure this guards against is not "the screen fails to
// blank" -- it is the screen CONTINUING to blank after the call is over, which
// makes the phone look broken.
//
// This reads the shipped source. It does not re-implement the rule.
import { readFileSync } from 'node:fs';

const FILE = 'ios/Sources/CapacitorTwilioVoicePlugin/CapacitorTwilioVoicePlugin.swift';
const raw = readFileSync(new URL(`../${FILE}`, import.meta.url), 'utf8');

// A check must never match its own explanatory comment.
// Blank comment CONTENT but keep the lines, so reported line numbers match the
// real file. A check that reports the wrong line is a check nobody trusts.
const src = raw
  .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
  .replace(/^(\s*)\/\/.*$/gm, '$1');

const lines = src.split('\n');
const fails = [];
const ok = [];

// Scan forward to the END OF THE ENCLOSING FUNCTION rather than a fixed number
// of lines. A fixed window produced a false positive on a correct site, and
// widening it blindly would have let a call in the NEXT function count.
function sameFunctionHas(idx, needle) {
  for (let i = idx; i < lines.length; i += 1) {
    if (i > idx && /^ {4}\}/.test(lines[i])) return false; // left the function
    if (lines[i].includes(needle)) return true;
  }
  return false;
}

// 1. Every mutation of activeCalls re-derives proximity within a few lines.
const MUTATION = /activeCalls\[[^\]]+\]\s*=|activeCalls\.removeValue|activeCalls\.removeAll/;
let mutations = 0;
lines.forEach((line, i) => {
  if (!MUTATION.test(line)) return;
  mutations += 1;
  if (sameFunctionHas(i, 'updateProximityMonitoring()')) ok.push(`mutation line ${i + 1}`);
  else fails.push(`activeCalls mutated at line ${i + 1} without re-deriving proximity`);
});
if (mutations < 4) fails.push(`only found ${mutations} activeCalls mutations - the matcher is broken, not the code`);

// 2. The route must be part of the decision, not just the call state.
if (!src.includes('builtInReceiver')) {
  fails.push('proximity does not consult the audio route - speaker/headphones would blank the screen');
}
if (!/routeChangeNotification/.test(src)) {
  fails.push('no routeChangeNotification observer - hitting speaker mid-call would not turn it off');
}

// 3. It must read activeCalls INSIDE the main-thread hop, not before it.
const body = src.slice(src.indexOf('private func updateProximityMonitoring'));
const hop = body.indexOf('DispatchQueue.main.async');
const read = body.indexOf('activeCalls.isEmpty');
if (hop === -1 || read === -1 || read < hop) {
  fails.push('activeCalls is read outside the main-thread hop - races with the CallKit delegates');
}

// 4. CallKit tearing everything down must turn it off.
const reset = src.indexOf('func providerDidReset');
if (reset === -1 || !src.slice(reset, reset + 400).includes('updateProximityMonitoring()')) {
  fails.push('providerDidReset does not re-derive proximity');
}

console.log(`${ok.length + 4 - fails.length} checks passed across ${mutations} mutation sites`);
if (fails.length) {
  for (const f of fails) console.error(`FAIL: ${f}`);
  process.exit(1);
}
