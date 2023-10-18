// api/hello.js

import { readFileSync } from 'fs';
import path from 'path';

export default function handler(req, res) {
  const file = path.join(process.cwd(), 'files', 'test.json');
  const stringified = readFileSync(file, 'utf8');

  res.setHeader('Content-Type', 'application/json');
  return res.end(stringified);
}