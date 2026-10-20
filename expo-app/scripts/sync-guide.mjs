#!/usr/bin/env node
// Zkopíruje kanonický guide.json z kořene repa do Expo appky.
// Jedna pravda o datech zůstává v root guide.json; tahle kopie je offline bundle.
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, '../../guide.json');
const target = resolve(here, '../src/data/guide.json');

const doc = JSON.parse(readFileSync(source, 'utf8'));
mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);

const steps = (doc.paths || []).reduce((n, p) => n + (p.steps || []).length, 0);
console.log(`guide.json → expo-app/src/data/guide.json (${(doc.paths || []).length} cest, ${steps} kroků)`);
