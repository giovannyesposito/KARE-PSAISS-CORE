/**
 * UI helpers — wrappers para @clack/prompts com identidade visual KARE-SPEC
 */

import * as clack from '@clack/prompts';

const CYAN  = '\x1b[36m';
const WHITE = '\x1b[37m';
const GREEN = '\x1b[32m';
const YELLOW= '\x1b[33m';
const RED   = '\x1b[31m';
const RESET = '\x1b[0m';

export const BANNER = `
${CYAN}  ██╗  ██╗ █████╗ ██████╗ ███████╗
  ██║ ██╔╝██╔══██╗██╔══██╗██╔════╝
  █████╔╝ ███████║██████╔╝█████╗
  ██╔═██╗ ██╔══██║██╔══██╗██╔══╝
  ██║  ██╗██║  ██║██║  ██║███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝${RESET}

${WHITE}  KARE-SPEC Installer${RESET}
`;

export function printBanner() {
  console.log(BANNER);
}

export function intro(message) {
  clack.intro(`${CYAN}◆ KARE-SPEC${RESET}  ${message}`);
}

export function outro(message) {
  clack.outro(`${GREEN}◆${RESET}  ${message}`);
}

export function log(message) {
  clack.log.info(message);
}

export function success(message) {
  clack.log.success(`${GREEN}${message}${RESET}`);
}

export function warn(message) {
  clack.log.warn(`${YELLOW}${message}${RESET}`);
}

export function error(message) {
  clack.log.error(`${RED}${message}${RESET}`);
}

export function step(message) {
  clack.log.step(message);
}

export function note(message, title = '') {
  clack.note(message, title);
}

export function cancel(message = 'Instalação cancelada.') {
  clack.cancel(message);
  process.exit(0);
}

export function spinner() {
  return clack.spinner();
}

export function isCancel(value) {
  return clack.isCancel(value);
}

export async function confirm(opts) {
  const result = await clack.confirm(opts);
  if (clack.isCancel(result)) cancel();
  return result;
}

export async function select(opts) {
  const result = await clack.select(opts);
  if (clack.isCancel(result)) cancel();
  return result;
}

export async function multiselect(opts) {
  const result = await clack.multiselect(opts);
  if (clack.isCancel(result)) cancel();
  return result;
}

export async function text(opts) {
  const result = await clack.text(opts);
  if (clack.isCancel(result)) cancel();
  return result;
}
