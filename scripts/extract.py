#!/usr/bin/env python3
"""Extract usage or long reports from Claude Code session transcripts.

Usage:
  python3 extract.py usage    '<glob-of-session-jsonl>'...
  python3 extract.py report   '<glob-of-session-jsonl>'   # prints every long
                              # assistant text (the run's own report usually
                              # arrives as one of these, at the end)

Globs, not hardcoded paths: point them at your own transcript directory, e.g.
~/.claude/projects/-Users-you-yourrepo-yourworktree/*.jsonl
Subagent sidechains live in the same directory as small extra JSONL files; the
main session is the largest one.
"""
import json, sys, glob, collections

mode = sys.argv[1]
paths = sum((glob.glob(a) for a in sys.argv[2:]), [])


def rows(p):
    for line in open(p):
        try:
            yield json.loads(line)
        except Exception:
            continue


if mode == 'report':
    for p in sorted(paths, key=lambda p: -__import__('os').path.getsize(p)):
        big = []
        for r in rows(p):
            if r.get('type') != 'assistant':
                continue
            content = r['message'].get('content')
            for b in content if isinstance(content, list) else []:
                if b.get('type') == 'text' and len(b.get('text', '')) > 150:
                    big.append((r['timestamp'][11:19], b['text']))
        for t, x in big:
            print('##', p, t, len(x)); print(x); print()
else:
    for p in paths:
        tot = collections.Counter(); models = collections.Counter()
        for r in rows(p):
            if r.get('type') != 'assistant':
                continue
            m = r['message']; u = m.get('usage') or {}
            if not m.get('model') or m['model'] == '<synthetic>':
                continue
            models[m['model']] += 1
            tot['in'] += u.get('input_tokens', 0)
            tot['out'] += u.get('output_tokens', 0)
            tot['cache_r'] += u.get('cache_read_input_tokens', 0)
            tot['cache_w'] += u.get('cache_creation_input_tokens', 0)
        print(p, dict(tot), dict(models))
