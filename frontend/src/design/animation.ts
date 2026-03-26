export const animation = { durations:{ fast:120, normal:240, slow:400 }, easing:{ standard:'cubic-bezier(0.4, 0.0, 0.2, 1)', emphasized:'cubic-bezier(0.2, 0.0, 0, 1)', decel:'cubic-bezier(0.0, 0, 0.2, 1)' } };
export const prefersReducedMotion = ()=> typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
