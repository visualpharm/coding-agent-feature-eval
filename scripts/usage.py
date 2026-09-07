#!/usr/bin/env python3
"""Sum token usage from Claude Code session transcript JSONL files.

Usage: python3 usage.py ~/.claude/projects/<project>/<session>.jsonl ... (globs ok)

Prints, per project directory: total input/output/cache-read/cache-write tokens,
model message counts, assistant turns, tool-use counts, first/last timestamps.

Counts are deduplicated by message id ACROSS the given files: Claude Code stores
multiple content records with the same message.id and identical usage, and a
resumed session file can repeat history — summing every assistant record
double-counts (an earlier version of this script did exactly that, inflating
this experiment's numbers until the audit corrected it; see scripts/audit.py).
GLM-through-Claude-Code sessions look the same (the harness is Claude Code; the
model field just says glm-5.3).
"""
import json, sys, glob, os, collections


def scan(paths):
    seen = set()
    tot = collections.Counter(); models = collections.Counter(); turns = 0
    tools = collections.Counter(); first = last = None
    for path in paths:
        for line in open(path):
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get('timestamp')
            if ts:
                first = first or ts; last = ts
            m = d.get('message', {})
            if d.get('type') != 'assistant':
                continue
            mid = m.get('id')
            if mid:
                if mid in seen:
                    continue
                seen.add(mid)
            u = m.get('usage') or {}
            tot['in'] += u.get('input_tokens', 0)
            tot['out'] += u.get('output_tokens', 0)
            tot['cache_r'] += u.get('cache_read_input_tokens', 0)
            tot['cache_w'] += u.get('cache_creation_input_tokens', 0)
            models[m.get('model')] += 1; turns += 1
            content = m.get('content')
            for b in content if isinstance(content, list) else []:
                if b.get('type') == 'tool_use':
                    tools[b['name']] += 1
    return tot, models, turns, tools, first, last


if __name__ == '__main__':
    for path in sum((glob.glob(a) for a in sys.argv[1:]), []):
        tot, models, turns, tools, f, l = scan([path])
        print(os.path.basename(os.path.dirname(path)), dict(tot), dict(models),
              'turns', turns, dict(tools), f, l)
